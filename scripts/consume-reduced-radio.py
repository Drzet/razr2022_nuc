#!/usr/bin/env python3
"""Exact immutable reduced radio producer check and reuse of native cpio builder.

The accepted broad-radio producer has a different source-identity key and
release. Do not alter its historic verifier or disguise the producer identity.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

RELEASE = "7.3.0-rc6-oneli-reduced1-g7f3865ee17c3"
COMMIT = "7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce"
CHECKS = {
    "Image": "279431f997fc2334d92760d47c01aec2b8e12cf47e6d149d6a078f2347c330e8",
    "kernel.config": "97ee634780847771163608e353e0086eceee6347ccd42a4d9d87d04f967981be",
    "radio-modules.tar.zst": "53223f163ebf1939192d85002939b4f201cff9abf7feb5160acf63c7eebbe908",
    "sm8475-motorola-oneli.dtb": "70d5c7b08ddda1c0974ac85e95bb1328528bb533c344a0681b5e95b88cd17435",
}
PREPOWER = "kernel/drivers/pci/pwrctrl/pci-pwrctrl-pwrseq.ko"
ATH11K = "kernel/drivers/net/wireless/ath/ath11k/ath11k_pci.ko"
HCI = "kernel/drivers/bluetooth/hci_uart.ko"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def inspect(producer, installed):
    r = Path(producer)
    m = Path(installed)
    for n, v in CHECKS.items():
        if sha(r / n) != v:
            raise ValueError("Wrong reduced producer digest: " + n)
    if (r / "kernel.release").read_text().strip() != RELEASE:
        raise ValueError("Wrong reduced release")
    identity = dict(line.split("=", 1) for line in
                    (r / "source-identity.txt").read_text().splitlines() if "=" in line)
    for name, wanted in {
        "kernel_source": COMMIT, "kernel_release": RELEASE,
        "LOCALVERSION": "-oneli-reduced1", "reduced_config_sha256": CHECKS["kernel.config"],
        "reused_accepted_dtb_sha256": CHECKS["sm8475-motorola-oneli.dtb"],
    }.items():
        if identity.get(name) != wanted:
            raise ValueError("Missing producer identity: " + name)
    sums = (r / "SHA256SUMS").read_text().splitlines()
    if len(sums) != 10:
        raise ValueError("Unexpected producer release file count")
    for line in sums:
        digest, relative = line.split(None, 1)
        if not re.fullmatch(r"[0-9a-f]{64}", digest) or sha(r / relative.removeprefix("./")) != digest:
            raise ValueError("Release SHA256SUMS failure: " + relative)
    cfg = (r / "kernel.config").read_text().splitlines()
    required = {"CONFIG_CFG80211=m","CONFIG_CFG80211_REQUIRE_SIGNED_REGDB=y",
                "CONFIG_CFG80211_USE_KERNEL_REGDB_KEYS=y","CONFIG_PCI_PWRCTRL_PWRSEQ=m",
                "CONFIG_ATH11K_PCI=m","CONFIG_BT_HCIUART=m","CONFIG_EXT4_FS=y",
                "CONFIG_VIRTIO_BLK=y","CONFIG_VIRTIO_NET=y","CONFIG_VIRTIO_MMIO=y",
                "CONFIG_SERIAL_AMBA_PL011_CONSOLE=y","CONFIG_RD_GZIP=y"}
    if not required.issubset(set(cfg)):
        raise ValueError("Reduced config lacks required guest/radio/signature closure")
    root = m / "lib/modules"
    if not root.is_dir() or {x.name for x in root.iterdir()} != {RELEASE}:
        raise ValueError("Unexpected installed releases")
    target = root / RELEASE
    hashes = {}
    for line in (r / "module-sha256.txt").read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (lib/modules/[^\s]+\.ko)", line)
        if not match or match.group(2) in hashes:
            raise ValueError("Bad module manifest entry")
        hashes[match.group(2)] = match.group(1)
    actual = {"lib/modules/" + RELEASE + "/" + p.relative_to(target).as_posix()
              for p in target.rglob("*.ko")}
    if len(actual) != 1179 or actual != set(hashes):
        raise ValueError("Wrong reduced module inventory")
    for relative, digest in hashes.items():
        if sha(m / relative) != digest:
            raise ValueError("Module byte mismatch: " + relative)
    deps = {}
    for line in (target / "modules.dep").read_text().splitlines():
        filename, colon, rhs = line.partition(":")
        if colon:
            deps[filename] = rhs.split()
    def closure(names):
        visited = {}
        def walk(name, stack=()):
            if name in stack or name not in deps or not (target / name).is_file():
                raise ValueError("Missing/cyclic module dependency: " + name)
            if name in visited:
                return
            for d in deps[name]:
                walk(d, (*stack, name))
            visited[name] = True
        for name in names:
            walk(name)
        return list(visited)
    early = closure([PREPOWER])
    radio = closure([PREPOWER, ATH11K, HCI])
    if early != [PREPOWER]:
        raise ValueError("Unexpected early module dependency closure")
    for mod in [PREPOWER, ATH11K, HCI]:
        blob = (target / mod).read_bytes()
        if blob[:6] != b"\x7fELF\x02\x01" or int.from_bytes(blob[18:20],"little") != 183:
            raise ValueError("Not an AArch64 module: " + mod)
        vermagic = subprocess.check_output(["modinfo","-F","vermagic",str(target / mod)],
                                           text=True).split()
        if not vermagic or vermagic[0] != RELEASE or "aarch64" not in vermagic:
            raise ValueError("Wrong module vermagic: " + mod)
    return {
        "schema": "oneli-reduced-userspace-inputs-v1", "kernel_commit": COMMIT,
        "kernel_release": RELEASE, "source_run": 39170486506,
        "source_artifact": 12153785196, "verified_module_count": len(hashes),
        "image_sha256": CHECKS["Image"], "config_sha256": CHECKS["kernel.config"],
        "dtb_sha256": CHECKS["sm8475-motorola-oneli.dtb"],
        "modules_archive_sha256": CHECKS["radio-modules.tar.zst"],
        "early_module_order": early, "radio_module_closure": radio,
        "early_deps": {name: deps[name] for name in early},
        "native_root_device": None, "hardware_tested": False,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--release", type=Path, required=True)
    p.add_argument("--installed", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--busybox", type=Path)
    args = p.parse_args()
    meta = inspect(args.release, args.installed)
    if args.busybox:
        spec = importlib.util.spec_from_file_location("radio_base", "scripts/package-radio-development.py")
        base = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(base)
        # Reuse the accepted cpio/ELF validation and initramfs construction, but
        # bind its callback to our *independently verified* reduced producer.
        base.RELEASE = RELEASE
        base.KERNEL = COMMIT
        base.CHECKS = {
            "Image": CHECKS["Image"], "kernel.config": CHECKS["kernel.config"],
            "sm8475-motorola-oneli.dtb": CHECKS["sm8475-motorola-oneli.dtb"],
            "radio-modules.tar.zst": CHECKS["radio-modules.tar.zst"],
        }
        base.verify = lambda _r, _m: inspect(_r, _m)
        base.build(args.release, args.installed, args.busybox, args.output)
        result = json.loads((args.output / "radio-inputs.json").read_text())
        if result["kernel_release"] != RELEASE or result["verified_module_count"] != 1179:
            raise ValueError("Early payload built with wrong release")
    else:
        args.output.parent.mkdir(exist_ok=True, parents=True)
        args.output.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    print("RAZR_REDUCED_PRODUCER_CONSUMER_PASS")

if __name__ == "__main__":
    main()
