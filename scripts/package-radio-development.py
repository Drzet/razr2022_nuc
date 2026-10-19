#!/usr/bin/env python3
"""Verify the accepted immutable radio bundle and produce a separate diskless development initramfs."""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

KERNEL = "7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce"
RELEASE = "7.3.0-rc6-g7f3865ee17c3"
CHECKS = {
    "Image": "0a28060210e747f8c63755142935feda101df4f5d9759f4e876bc2bb1373fb2e",
    "sm8475-motorola-oneli.dtb": "70d5c7b08ddda1c0974ac85e95bb1328528bb533c344a0681b5e95b88cd17435",
    "kernel.config": "e10f77e9c982a4c3c81c94e69922ad8ae623b71e99df88e40c415e5a6fc0b273",
    "Module.symvers": "5802d8bb9cb077c61dcf0d7b2bdc8d32793329389156b3b312e7339f9a3d3151",
    "radio-modules.tar.zst": "8a6891d140587ca56ca071beb82a473a21b21dd3874fba4ada36465d519819d5",
}
PREPOWER = "kernel/drivers/pci/pwrctrl/pci-pwrctrl-pwrseq.ko"
ATH11K = "kernel/drivers/net/wireless/ath/ath11k/ath11k_pci.ko"
HCI = "kernel/drivers/bluetooth/hci_uart.ko"

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify(release_dir, modules):
    r = Path(release_dir)
    m = Path(modules)
    for name, expected in CHECKS.items():
        if sha(r/name) != expected:
            raise ValueError("wrong accepted release digest: " + name)
    if (r/"kernel.release").read_text().strip() != RELEASE:
        raise ValueError("release mismatch")
    identity = dict(line.split("=",1) for line in (r/"source-identity.txt").read_text().splitlines() if "=" in line)
    if identity.get("kernel_sha") != KERNEL or identity.get("kernel_release") != RELEASE:
        raise ValueError("kernel source mismatch")
    for line in (r/"SHA256SUMS").read_text().splitlines():
        digest, file = line.split(None,1)
        if sha(r/file.removeprefix("./")) != digest:
            raise ValueError("release checksum mismatch " + file)
    root = m/"lib/modules"/RELEASE
    if not root.is_dir() or sorted(x.name for x in (m/"lib/modules").iterdir()) != [RELEASE]:
        raise ValueError("mixed module releases")
    entries = set()
    for line in (r/"module-sha256.txt").read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (lib/modules/.+\.ko)", line)
        if not match or match.group(2) in entries:
            raise ValueError("malformed module inventory")
        entries.add(match.group(2))
        if sha(m/match.group(2)) != match.group(1):
            raise ValueError("module SHA mismatch " + match.group(2))
    actual = {"lib/modules/"+RELEASE+"/"+f.relative_to(root).as_posix() for f in root.rglob("*.ko")}
    if entries != actual:
        raise ValueError("incomplete installed module inventory")
    deps = {}
    for line in (root/"modules.dep").read_text().splitlines():
        file,sep,tails = line.partition(":")
        if sep:
            deps[file] = tails.split()
    def closure(names):
        result = {}
        def walk(name,ancestors=()):
            if name in ancestors:
                raise ValueError("cyclic modules.dep")
            if name in result:
                return
            if name not in deps or not (root/name).is_file():
                raise ValueError("missing dependency " + name)
            for dependency in deps[name]:
                walk(dependency,(*ancestors,name))
            result[name] = True
        for n in names:
            walk(n)
        return list(result)
    pre = closure([PREPOWER])
    radio = closure([PREPOWER,ATH11K,HCI])
    for path in (PREPOWER,ATH11K,HCI):
        mod = root/path
        elf = mod.read_bytes()
        if elf[:6] != b"\x7fELF\x02\x01" or int.from_bytes(elf[18:20],"little") != 183:
            raise ValueError("module is not AArch64: "+path)
        vermagic = subprocess.check_output(["modinfo","-F","vermagic",str(mod)],text=True).split()
        if not vermagic or vermagic[0] != RELEASE or "aarch64" not in vermagic:
            raise ValueError("module ABI mismatch: "+path)
    return dict(schema="oneli-radio-development-inputs-v1",kernel_commit=KERNEL,
                kernel_release=RELEASE,verified_module_count=len(entries),
                image_sha256=CHECKS["Image"],dtb_sha256=CHECKS["sm8475-motorola-oneli.dtb"],
                config_sha256=CHECKS["kernel.config"],module_tar_sha256=CHECKS["radio-modules.tar.zst"],
                early_module_order=pre,radio_module_closure=radio,
                early_deps={name:deps[name] for name in pre},
                root_device=None,native_storage_ready=False,
                board_radio_hardware_tested=False)

def build(release_dir,modules,busybox,output):
    meta = verify(release_dir,modules)
    spec = importlib.util.spec_from_file_location("native_diag","scripts/build-native-diag.py")
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    binary = Path(busybox).read_bytes()
    native.assert_elf_static_arm64(binary)
    out=Path(output)
    out.mkdir(exist_ok=False,parents=True)
    entries=[native.record("bin","dir"),native.record("bin/busybox","file",binary),
             native.record("bin/sh","link",b"busybox",0o777),native.record("dev","dir"),
             native.record("dev/console","char",mode=0o600,major=5,minor=1),
             native.record("dev/null","char",mode=0o666,major=1,minor=3),
             native.record("proc","dir"),native.record("sys","dir"),
             native.record("run","dir"),native.record("tmp","dir",mode=0o1777)]
    prefix="lib/modules/"+RELEASE+"/"
    init='''#!/bin/sh
PATH=/bin
export PATH
BB=/bin/busybox
say() { printf '%s\\n' "$*" > /dev/console 2>/dev/null || :; }
for entry in 'proc /proc proc' 'sysfs /sys sysfs' 'devtmpfs /dev devtmpfs' 'tmpfs /run tmpfs'; do
    set -- $entry
    "$BB" mount -t "$3" "$1" "$2" || say "RADIO_EARLY_MOUNT_FAILED=$2"
done
say "RADIO_EARLY_PID1=$$"
say "RADIO_EARLY_RELEASE=$("$BB" uname -r)"
'''
    for name in meta["early_module_order"]:
        init += f'''if "$BB" insmod /{prefix}{name}; then
    say "RADIO_EARLY_INSMOD_OK={name}"
else
    say "RADIO_EARLY_INSMOD_FAILED={name}"
fi
'''
        full=prefix+name
        parts=Path(full).parts
        present={entry[0] for entry in entries}
        for i in range(1,len(parts)):
            parent="/".join(parts[:i])
            if parent not in present:
                entries.append(native.record(parent,"dir"))
                present.add(parent)
        entries.append(native.record(full,"file",(Path(modules)/full).read_bytes(),mode=0o644))
    init += '''say RADIO_EARLY_READY_V1
cmdline=$($BB cat /proc/cmdline 2>/dev/null || :)
compat=$($BB tr '\\000' '\\n' </proc/device-tree/compatible 2>/dev/null || :)
case "$cmdline" in
  *razr.radio_qemu_shutdown=1*)
    case "$compat" in
      *linux,dummy-virt*) say RADIO_EARLY_QEMU_SHUTDOWN; "$BB" poweroff -f || : ;;
    esac ;;
esac
say RADIO_EARLY_HOLD
while :; do "$BB" sleep 60; done
'''
    entries.append(native.record("init","file",init.encode()))
    cpio=out/"radio-early.cpio"
    cpio.write_bytes(native.archive(entries))
    compressed=out/"radio-early.cpio.gz"
    compressed.write_bytes(gzip.compress(cpio.read_bytes(),compresslevel=9,mtime=0))
    native.verify_payload(cpio,compressed)
    meta.update(init_sha256=hashlib.sha256(init.encode()).hexdigest(),
                busybox_sha256=hashlib.sha256(binary).hexdigest(),
                early_cpio_sha256=sha(cpio),early_gzip_sha256=sha(compressed))
    (out/"radio-inputs.json").write_text(json.dumps(meta,sort_keys=True,indent=2)+"\n")
    print("RADIO_EARLY_BUILD_PASS")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for arg in ("release","modules","busybox","output"):
        p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    build(a.release,a.modules,a.busybox,a.output)
