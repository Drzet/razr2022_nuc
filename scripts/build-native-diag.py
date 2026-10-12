#!/usr/bin/env python3
"""Deterministic, self-checking early diagnostic initramfs for the Boot v1 wire contract."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import subprocess

PACKAGE_SHA256 = "c833be48abfa16bc19c4966ec93e289ff1ce5d2f1476cad3a57bd105378cd15c"
PACKAGE_VERSION = "1:1.37.0-6+b9"
MARKER = "RAZR_NATIVE_DIAG_READY_V1"
INIT = r'''#!/bin/sh
PATH=/bin
export PATH
BB=/bin/busybox
failures=0
for spec in 'proc /proc proc' 'sysfs /sys sysfs' 'devtmpfs /dev devtmpfs' 'tmpfs /run tmpfs'; do
    set -- $spec
    if ! "$BB" mount -t "$3" "$1" "$2"; then
        failures=$((failures + 1))
        printf 'MOUNT_FAILURE %s %s %s\n' "$1" "$2" "$3" >/dev/console 2>/dev/null || :
    fi
done
"$BB" mkdir -p /run/oneli-diag
log=/run/oneli-diag/000001.log
: > "$log"
record() {
    printf '%s\n' "$*" >> "$log"
    printf '%s\n' "$*" >/dev/console 2>/dev/null || :
}
record "RAZR_NATIVE_DIAG_SEQUENCE=000001"
record "RAZR_NATIVE_DIAG_PID1=$$"
record "RAZR_NATIVE_DIAG_MOUNT_FAILURES=$failures"
record "RAZR_NATIVE_DIAG_KERNEL=$("$BB" uname -a)"
record "RAZR_NATIVE_DIAG_RELEASE=$("$BB" uname -r)"
if [ -r /proc/cmdline ]; then
    cmdline=$("$BB" cat /proc/cmdline)
    record "RAZR_NATIVE_DIAG_CMDLINE=$cmdline"
else
    cmdline=''
    record "READ_FAILURE /proc/cmdline"
fi
if [ -r /proc/device-tree/compatible ]; then
    compat=$("$BB" tr '\000' '\n' </proc/device-tree/compatible)
    record "RAZR_NATIVE_DIAG_DT_COMPAT_BEGIN"
    record "$compat"
    record "RAZR_NATIVE_DIAG_DT_COMPAT_END"
else
    compat=''
    record "READ_FAILURE /proc/device-tree/compatible"
fi
record "RAZR_NATIVE_DIAG_PROBE_ERRORS_BEGIN"
if "$BB" dmesg > /run/oneli-diag/dmesg.raw 2>/run/oneli-diag/dmesg.error; then
    "$BB" grep -iE 'fail|error|probe|timeout|defer' /run/oneli-diag/dmesg.raw | "$BB" tail -n 80 >> "$log" || :
else
    record "READ_FAILURE kernel_dmesg"
    "$BB" cat /run/oneli-diag/dmesg.error >> "$log" 2>/dev/null || :
fi
record "RAZR_NATIVE_DIAG_PROBE_ERRORS_END"
record "RAZR_NATIVE_DIAG_READY_V1"
printf '%s\n' 'oneli-diag: RAZR_NATIVE_DIAG_READY_V1' >/dev/kmsg 2>/dev/null || :
case "$cmdline" in
    *razr.diag_test_shutdown=1*)
        case "$compat" in
            *linux,dummy-virt*)
                record "RAZR_NATIVE_DIAG_QEMU_SHUTDOWN"
                "$BB" sync
                "$BB" poweroff -f
                record "RAZR_NATIVE_DIAG_SHUTDOWN_FAILED"
                ;;
            *) record "RAZR_NATIVE_DIAG_SHUTDOWN_DENIED_NON_QEMU_DT" ;;
        esac
        ;;
esac
record "RAZR_NATIVE_DIAG_HOLD"
while :; do "$BB" sleep 60; done
'''

def sha(data):
    return hashlib.sha256(data).hexdigest()

def digest(path):
    return sha(Path(path).read_bytes())

def assert_elf_static_arm64(data):
    if data[:4] != b"\x7fELF" or data[4] != 2 or data[5] != 1:
        raise ValueError("BusyBox must be a little-endian 64-bit ELF")
    if struct.unpack_from("<H", data, 18)[0] != 183:
        raise ValueError("BusyBox ELF is not AArch64")
    phoff = struct.unpack_from("<Q", data, 32)[0]
    phentsize = struct.unpack_from("<H", data, 54)[0]
    phnum = struct.unpack_from("<H", data, 56)[0]
    if phoff == 0 or phentsize < 56 or phnum == 0 or phoff + phnum * phentsize > len(data):
        raise ValueError("invalid ELF program header table")
    if any(struct.unpack_from("<I", data, phoff + i * phentsize)[0] == 3 for i in range(phnum)):
        raise ValueError("ELF has PT_INTERP: BusyBox must be static")

def record(path, kind, data=b"", mode=0o755, major=0, minor=0):
    return (path, kind, data, mode, major, minor)

def archive(entries):
    out = bytearray()
    for ino, (name, kind, data, permissions, major, minor) in enumerate(
            sorted(entries, key=lambda x: x[0].encode("utf-8")), 1):
        assert not name.startswith("/") and ".." not in name.split("/")
        mode = {"dir": stat.S_IFDIR, "file": stat.S_IFREG,
                "link": stat.S_IFLNK, "char": stat.S_IFCHR}[kind] | permissions
        name_b = name.encode("utf-8") + b"\0"
        fields = (ino, mode, 0, 0, 2 if kind == "dir" else 1, 0, len(data),
                  0, 0, major, minor, len(name_b), 0)
        out.extend(b"070701" + b"".join(("%08x" % field).encode("ascii") for field in fields))
        out.extend(name_b)
        out.extend(b"\0" * (-len(out) % 4))
        out.extend(data)
        out.extend(b"\0" * (-len(out) % 4))
    trailer = b"TRAILER!!!\0"
    fields = (0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, len(trailer), 0)
    out.extend(b"070701" + b"".join(("%08x" % field).encode("ascii") for field in fields))
    out.extend(trailer)
    out.extend(b"\0" * (-len(out) % 4))
    return bytes(out)

def unpack(raw):
    pos = 0
    found = []
    while True:
        start = pos
        if raw[pos:pos+6] != b"070701":
            raise ValueError("missing newc magic at byte " + str(pos))
        fields = [int(raw[pos+6+i*8:pos+14+i*8], 16) for i in range(13)]
        ino, mode, uid, gid, nlink, mtime, size, _, _, major, minor, namesize, check = fields
        pos += 110
        if not (0 < namesize < 4096) or pos + namesize > len(raw):
            raise ValueError("bad newc name bounds")
        name_b = raw[pos:pos+namesize]
        if not name_b.endswith(b"\0"):
            raise ValueError("missing NUL in filename")
        name = name_b[:-1].decode("utf-8")
        pos = (pos + namesize + 3) & ~3
        if pos + size > len(raw):
            raise ValueError("bad newc data bounds")
        data = raw[pos:pos+size]
        pos = (pos + size + 3) & ~3
        if (uid, gid, mtime, check) != (0, 0, 0, 0):
            raise ValueError("nondeterministic newc metadata")
        if name == "TRAILER!!!":
            if size or raw[pos:].strip(b"\0"):
                raise ValueError("bad trailer")
            return found
        if not name or name.startswith("/") or ".." in name.split("/"):
            raise ValueError("unsafe newc pathname")
        found.append((name, mode, data, major, minor))

def validate_archive(path):
    raw = Path(path).read_bytes()
    entries = unpack(raw)
    names = [x[0] for x in entries]
    if len(names) != len(set(names)) or names != sorted(names, key=lambda s: s.encode("utf-8")):
        raise ValueError("newc entry names not unique/C-sorted")
    data = {n: (m, d) for n, m, d, _, _ in entries}
    if any(n not in data for n in ("init", "bin/busybox", "bin/sh", "dev",
                                   "proc", "sys", "run", "tmp")):
        raise ValueError("missing mandatory paths")
    if not data["init"][0] & 0o111 or not stat.S_ISREG(data["init"][0]):
        raise ValueError("/init not executable regular file")
    if not stat.S_ISLNK(data["bin/sh"][0]) or data["bin/sh"][1] != b"busybox":
        raise ValueError("/bin/sh is not the expected symlink")
    assert_elf_static_arm64(data["bin/busybox"][1])
    for n, m, d, major, minor in entries:
        if n in ("dev/console", "dev/null") and not stat.S_ISCHR(m):
            raise ValueError(n + " must be char device")
        if n == "dev/console" and (major, minor) != (5, 1):
            raise ValueError("bad /dev/console")
        if n == "dev/null" and (major, minor) != (1, 3):
            raise ValueError("bad /dev/null")
    return data, entries

def contract_file(path):
    contract = json.loads(Path(path).read_text())
    if contract["schema"] != "oneli-native-early-initramfs-interface-v1":
        raise ValueError("wrong Boot wire interface")
    return contract

def verify_config(path):
    lines = set(Path(path).read_text().splitlines())
    required = ("CONFIG_ARM64=y", "CONFIG_BLK_DEV_INITRD=y", "CONFIG_RD_GZIP=y",
                "CONFIG_BINFMT_SCRIPT=y", "CONFIG_PROC_FS=y", "CONFIG_SYSFS=y",
                "CONFIG_DEVTMPFS=y", "CONFIG_TMPFS=y", "CONFIG_SERIAL_AMBA_PL011=y",
                "CONFIG_SERIAL_AMBA_PL011_CONSOLE=y", "CONFIG_SERIAL_QCOM_GENI=y",
                "CONFIG_SERIAL_QCOM_GENI_CONSOLE=y")
    missing = [v for v in required if v not in lines]
    if missing:
        raise ValueError("accepted generated config missing builtin requirement: " + ", ".join(missing))
    return list(required)

def build(a):
    c = contract_file(a.contract)
    k = c["kernel"]
    for p, expected in ((a.image, k["image_sha256"]),
                        (a.config, k["config_sha256"]),
                        (a.dtb, k["board_dtb_sha256"])):
        if digest(p) != expected:
            raise ValueError("accepted kernel file digest mismatch: " + str(p))
    config_proof = verify_config(a.config)
    binary = Path(a.busybox).read_bytes()
    assert_elf_static_arm64(binary)
    root = Path(a.output)
    if root.exists():
        raise ValueError("output must be a new directory")
    root.mkdir(parents=True)
    init = INIT.encode("utf-8")
    entries = [
        record("bin", "dir"), record("bin/busybox", "file", binary),
        record("bin/sh", "link", b"busybox", 0o777),
        record("dev", "dir"), record("dev/console", "char", mode=0o600, major=5, minor=1),
        record("dev/null", "char", mode=0o666, major=1, minor=3),
        record("init", "file", init), record("proc", "dir"),
        record("run", "dir"), record("sys", "dir"), record("tmp", "dir", mode=0o1777)]
    cpio = root / c["userspace_payload"]["cpio_path"]
    compressed = root / c["userspace_payload"]["compressed_path"]
    cpio.write_bytes(archive(entries))
    with compressed.open("wb") as dst:
        subprocess.run(["gzip", "-n", "-9", "-c", str(cpio)], stdout=dst, check=True)
    verify_payload(cpio, compressed)
    summary = {"schema": "oneli-native-diag-build-evidence-v1",
               "interface_blob_git_sha1": a.interface_blob,
               "kernel_commit": k["commit"], "kernel_release": k["release"],
               "kernel_image_sha256": k["image_sha256"],
               "kernel_config_sha256": k["config_sha256"],
               "board_dtb_sha256": k["board_dtb_sha256"],
               "verified_builtin_config": config_proof,
               "busybox_elf_sha256": sha(binary),
               "busybox_deb_sha256": PACKAGE_SHA256,
               "busybox_package_revision": PACKAGE_VERSION,
               "cpio_sha256": digest(cpio), "compressed_sha256": digest(compressed),
               "init_sha256": sha(init),
               "no_disk_mount_or_firmware_module_autoload": True}
    (root / "build-inputs.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n")
    (root / "newc-listing.json").write_text(
        json.dumps([{"path": n, "mode": oct(m), "uid": 0, "gid": 0, "mtime": 0,
                     "sha256": sha(d) if stat.S_ISREG(m) else None}
                    for n, m, d, _, _ in validate_archive(cpio)[1]],
                   indent=2)+"\n")
    print("RAZR_NATIVE_DIAG_CPIO_BUILD_PASS")

def verify_payload(cpio, compressed):
    data, entries = validate_archive(cpio)
    gz = Path(compressed).read_bytes()
    if len(gz) < 10 or gz[:4] != b"\x1f\x8b\x08\x00" or gz[4:8] != b"\0"*4:
        raise ValueError("gzip not -n/mtime=0")
    if gzip.decompress(gz) != Path(cpio).read_bytes():
        raise ValueError("gzip payload differs from raw cpio")
    return data, entries

def finalize(a):
    c = contract_file(a.contract)
    root = Path(a.directory)
    build_input = json.loads((root / "build-inputs.json").read_text())
    if build_input["interface_blob_git_sha1"] != a.interface_blob:
        raise ValueError("contract has changed since build")
    raw_name = c["userspace_payload"]["cpio_path"]
    compressed_name = c["userspace_payload"]["compressed_path"]
    files, _ = verify_payload(root/raw_name, root/compressed_name)
    log = root / "qemu-serial.log"
    serial = log.read_bytes()
    expected = (MARKER, "RAZR_NATIVE_DIAG_PID1=1",
                "RAZR_NATIVE_DIAG_RELEASE=" + c["kernel"]["release"],
                "RAZR_NATIVE_DIAG_MOUNT_FAILURES=0",
                "RAZR_NATIVE_DIAG_QEMU_SHUTDOWN", "reboot: Power down")
    for s in expected:
        if s.encode() not in serial:
            raise ValueError("actual QEMU serial missing " + s)
    if (root / "qemu-exit-code.txt").read_text().strip() != "0":
        raise ValueError("QEMU did not exit zero")
    p = c["userspace_payload"]
    manifest = {
        "schema": "oneli-native-diag-payload-v1", "interface": c["schema"],
        "kernel_commit": c["kernel"]["commit"], "kernel_release": c["kernel"]["release"],
        "kernel_image_sha256": c["kernel"]["image_sha256"],
        "board_dtb_sha256": c["kernel"]["board_dtb_sha256"],
        "cpio_relative_path": raw_name, "cpio_sha256": digest(root/raw_name),
        "compressed_relative_path": compressed_name, "compressed_sha256": digest(root/compressed_name),
        "compression": "gzip", "cpio_format": "newc", "numeric_owner": {"uid": 0, "gid": 0},
        "init_path": "/init", "init_sha256": sha(files["init"][1]),
        "modules": [], "module_requirement_rationale":
        "No module insertion or storage/network operations in diagnostic /init. Config-proven "
        "built-in initrd/gzip, script execution, proc/sysfs, devtmpfs, tmpfs, PL011 (QEMU), "
        "and Qualcomm GENI console (oneli source path); all additional compiled modules excluded.",
        "firmware": [], "firmware_requirement_rationale":
        "Only built-in early printk/console, virtual memory filesystems and BusyBox commands "
        "are requested; /init does not activate GPU, VPU, modem, UFS, USB, charging or vendor "
        "remoteproc/secure-firmware services. Probe failures are recorded, not hidden.",
        "tool_provenance": {
            "name": "Debian busybox-static arm64 + host Python/gzip",
            "version": PACKAGE_VERSION,
            "source": "Debian trixie pool/main/b/busybox and project scripts/build-native-diag.py",
            "sha256_or_package_revision": PACKAGE_SHA256,
            "busybox_elf_sha256": build_input["busybox_elf_sha256"],
            "host_python": subprocess.check_output(["python3", "--version"], text=True).strip(),
            "host_gzip": subprocess.check_output(["gzip", "--version"], text=True).splitlines()[0],
            "kernel_config_sha256": build_input["kernel_config_sha256"],
            "builtins_verified": build_input["verified_builtin_config"]
        },
        "qemu_validation": {
            "result": "pass", "qemu_generated_dtb": True, "debian_rootfs_used": False,
            "pid1_verified": True, "kernel_release_verified": True, "ready_marker": MARKER,
            "exit_code": 0, "serial_log_relative_path": "qemu-serial.log",
            "serial_log_sha256": sha(serial), "test_command_relative_path": "qemu-command.txt"
        }
    }
    for field, specification in p["manifest_field_contract"].items():
        if field not in manifest:
            raise ValueError("contract field missing " + field)
        if specification["type"] == "literal" and manifest[field] != specification["value"]:
            raise ValueError("contract literal mismatch " + field)
        if specification["type"] == "sha256-hex" and not re.fullmatch("[0-9a-f]{64}", manifest[field]):
            raise ValueError("invalid digest " + field)
    for key, val in p["manifest_field_contract"]["qemu_validation"]["expected"].items() if False else []:
        pass
    for key, val in p["manifest_field_contract"]["qemu_validation"]["expected"].items():
        if manifest["qemu_validation"][key] != val:
            raise ValueError("invalid qemu evidence " + key)
    out = root / p["manifest_path"]
    out.write_text(json.dumps(manifest, sort_keys=True, indent=2)+"\n")
    verify_manifest(out, a.contract)
    print("RAZR_NATIVE_DIAG_FINALIZE_PASS")

def verify_manifest(path, contract):
    c = contract_file(contract)
    root = Path(path).parent
    m = json.loads(Path(path).read_text())
    for key in c["userspace_payload"]["required_manifest_keys"]:
        if key not in m:
            raise ValueError("missing mandatory manifest key " + key)
    for key, value in c["userspace_payload"]["manifest_field_contract"].items():
        if value["type"] == "literal" and m[key] != value["value"]:
            raise ValueError("manifest literal mismatch " + key)
        if value["type"] == "sha256-hex" and not re.fullmatch("[0-9a-f]{64}", m[key]):
            raise ValueError("manifest sha invalid " + key)
    for k in ("cpio_relative_path", "compressed_relative_path"):
        p = Path(m[k])
        if p.is_absolute() or ".." in p.parts or len(p.parts) != 1:
            raise ValueError("unsafe manifest path")
    cpio = root / m["cpio_relative_path"]
    compressed = root / m["compressed_relative_path"]
    files, _ = verify_payload(cpio, compressed)
    for key, path in (("cpio_sha256", cpio), ("compressed_sha256", compressed)):
        if m[key] != digest(path):
            raise ValueError("payload hash mismatch " + key)
    if m["init_sha256"] != sha(files["init"][1]):
        raise ValueError("init hash mismatch")
    q = m["qemu_validation"]
    for key, val in c["userspace_payload"]["manifest_field_contract"]["qemu_validation"]["expected"].items():
        if q[key] != val:
            raise ValueError("QEMU contract mismatch " + key)
    log_path = Path(q["serial_log_relative_path"])
    if log_path.is_absolute() or ".." in log_path.parts or len(log_path.parts) != 1:
        raise ValueError("unsafe serial log path")
    if digest(root/log_path) != q["serial_log_sha256"]:
        raise ValueError("serial log digest mismatch")
    if m["modules"] or m["firmware"]:
        raise ValueError("minimal diagnostic profile cannot include implicit modules/firmware")
    if not m["module_requirement_rationale"] or not m["firmware_requirement_rationale"]:
        raise ValueError("missing zero-requirement rationales")
    print("RAZR_NATIVE_DIAG_MANIFEST_VERIFY_PASS")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="action", required=True)
    b = sub.add_parser("build")
    for arg in ("contract", "image", "config", "dtb", "busybox", "output", "interface-blob"):
        b.add_argument("--"+arg, required=True)
    f = sub.add_parser("finalize")
    for arg in ("contract", "directory", "interface-blob"):
        f.add_argument("--"+arg, required=True)
    v = sub.add_parser("verify")
    v.add_argument("--contract", required=True)
    v.add_argument("--manifest", required=True)
    a = p.parse_args()
    {"build": build, "finalize": finalize,
     "verify": lambda z: verify_manifest(z.manifest, z.contract)}[a.action](a)

if __name__ == "__main__":
    main()
