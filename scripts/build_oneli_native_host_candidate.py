#!/usr/bin/env python3
"""Fail-closed, unsigned oneli Android-v4 *host-only* diagnostic packer.

Inputs must come from independently hashed accepted kernel and Userspace artifacts.
Never writes a partition, runs adb/fastboot, or asserts native bootability.
AOSP's independently pinned unpack_bootimg.py must inspect the produced images.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile

PAGE = 4096
IMAGE_SHA = "3a8fa9620e0fc8de68ce8db45dacdfd811a2ba2c9718f9cddee3893ec9af0939"
CONFIG_SHA = "c86c04cc707889c66f8e4a485d1bff70819c1747150cb211836f07efb9fff90e"
DTB_SHA = "d3c9abcea9950200babbcf6c979073dc94c6af5cac68578540ad570db4a14a03"
KERNEL_COMMIT = "2b5acf108ae37040ac1e652e029bb37f5609e886"
RELEASE = "7.3.0-rc6-g2b5acf108ae3"
CPIO_SHA = "6805a3482e2946c3aca60f52c9c91711f5cde5720e30a5230df3fb4829e2ea4e"
GZIP_SHA = "3d7a08022bdff062455099d509d54c9aa571cb9c289d89a431b7edb892846f3b"
INIT_SHA = "31cba1801f6ecbd17a31b5b81755d6dc51071a8587bbb782ceecc3ec905328c4"
LOG_SHA = "84152346608e01fd719d60dde36c529bd4e78129845df0bd239d26206f782fa4"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_sha(path, expected):
    content = path.read_bytes()
    require(digest(content) == expected, f"SHA256 mismatch: {path}")
    return content


def aligned(n):
    return (n + 3) & ~3


def paged(data):
    return data + bytes((-len(data)) % PAGE)


def check_simple(name):
    require(isinstance(name, str) and name and name not in (".", ".."), "unsafe empty path")
    require(not name.startswith("/") and not name.startswith("./") and "\\" not in name, "unsafe relative path")
    require(all(x not in ("", ".", "..") for x in name.split("/")), "path traversal")
    return name


def newc_parse(data):
    p, result, names = 0, {}, []
    while p < len(data):
        require(p % 4 == 0, "newc header not 4-byte aligned")
        hdr = data[p:p + 110]
        require(len(hdr) == 110 and hdr[:6] == b"070701", "unsupported/truncated newc header")
        try:
            fields = [int(hdr[6 + i * 8:14 + i * 8], 16) for i in range(13)]
        except ValueError as e:
            raise ValueError("malformed newc integer") from e
        ino, mode, uid, gid, nlink, mtime, size, _, _, _, _, namesize, check = fields
        require(0 < namesize <= 4096 and check == 0 and nlink >= 1, "newc invalid metadata")
        name_start = p + 110
        name_end = name_start + namesize
        require(name_end <= len(data), "newc pathname truncated")
        pathname = data[name_start:name_end]
        require(pathname[-1:] == b"\0" and b"\0" not in pathname[:-1], "newc pathname NUL")
        name = pathname[:-1].decode("utf-8")
        start = aligned(name_end)
        end = start + size
        require(end <= len(data) and not any(data[name_end:start]), "newc data/alignment invalid")
        content = data[start:end]
        require(not any(data[end:aligned(end)]), "newc padding nonzero")
        p = aligned(end)
        if name == "TRAILER!!!":
            require(size == 0, "newc trailer cannot carry data")
            require(not any(data[p:]), "newc bytes after trailer")
            break
        check_simple(name)
        require(name not in result, "duplicate newc pathname")
        require(uid == gid == mtime == 0, "newc must have numeric root ownership and epoch timestamps")
        kind = mode & 0o170000
        require(kind in (0o100000, 0o040000, 0o120000, 0o020000), "newc unexpected file type")
        if kind == 0o120000:
            link = content.decode("utf-8")
            require(not link.startswith("/") and ".." not in link.split("/"), "newc symlink escapes root")
        result[name] = {"mode": mode, "bytes": content, "kind": kind}
        names.append(name)
    else:
        raise ValueError("newc missing TRAILER!!!")
    require(names == sorted(names), "newc filenames not C-sorted")
    return result


def newc_empty():
    fields = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, len("TRAILER!!!") + 1, 0]
    head = b"070701" + b"".join(f"{v:08x}".encode("ascii") for v in fields)
    return head + b"TRAILER!!!\0" + bytes((-len(head) - len("TRAILER!!!") - 1) % 4)


def ensure_ums_manifest(payload_dir, manifest):
    expected = {
        "schema": "oneli-native-diag-payload-v1",
        "interface": "oneli-native-early-initramfs-interface-v1",
        "kernel_commit": KERNEL_COMMIT,
        "kernel_release": RELEASE,
        "kernel_image_sha256": IMAGE_SHA,
        "board_dtb_sha256": DTB_SHA,
        "cpio_relative_path": "oneli-diag-initramfs.cpio",
        "compressed_relative_path": "oneli-diag-initramfs.cpio.gz",
        "cpio_sha256": CPIO_SHA,
        "compressed_sha256": GZIP_SHA,
        "init_path": "/init",
        "init_sha256": INIT_SHA,
        "cpio_format": "newc",
        "compression": "gzip",
        "numeric_owner": {"uid": 0, "gid": 0},
    }
    for key, value in expected.items():
        require(manifest.get(key) == value, f"Userspace manifest {key} conflict")
    for key in ("module_requirement_rationale", "firmware_requirement_rationale"):
        require(isinstance(manifest.get(key), str) and manifest[key].strip(), f"missing {key}")
    require(manifest.get("modules") == [] and manifest.get("firmware") == [], "minimal profile requires explicit empty module/firmware arrays")
    require(isinstance(manifest.get("tool_provenance"), dict) and manifest["tool_provenance"], "missing tool provenance")
    q = manifest.get("qemu_validation") or {}
    for key, value in {
        "result": "pass", "qemu_generated_dtb": True, "debian_rootfs_used": False,
        "pid1_verified": True, "kernel_release_verified": True,
        "ready_marker": "RAZR_NATIVE_DIAG_READY_V1", "exit_code": 0,
        "serial_log_sha256": LOG_SHA
    }.items():
        require(q.get(key) == value, f"Userspace QEMU evidence {key} conflict")
    log_name = check_simple(q.get("serial_log_relative_path"))
    require("/" not in log_name, "serial log is not a direct payload file")
    log = read_sha(payload_dir / log_name, LOG_SHA)
    for token in (b"RAZR_NATIVE_DIAG_READY_V1", b"RAZR_NATIVE_DIAG_PID1=1",
                  b"RAZR_NATIVE_DIAG_MOUNT_FAILURES=0", b"RAZR_NATIVE_DIAG_QEMU_SHUTDOWN",
                  b"reboot: Power down", RELEASE.encode()):
        require(token in log, "QEMU serial evidence lacks " + token.decode())
    require((payload_dir / "qemu-exit-code.txt").read_text().strip() == "0", "positive QEMU exited nonzero")
    hold = (payload_dir / "qemu-hold-serial.log").read_bytes()
    require(b"RAZR_NATIVE_DIAG_HOLD" in hold and b"RAZR_NATIVE_DIAG_QEMU_SHUTDOWN" not in hold, "hold-mode proof invalid")
    require((payload_dir / "qemu-hold-exit-code.txt").read_text().strip() == "124", "hold-mode bounded host timeout invalid")
    raw = read_sha(payload_dir / "oneli-diag-initramfs.cpio", CPIO_SHA)
    compressed = read_sha(payload_dir / "oneli-diag-initramfs.cpio.gz", GZIP_SHA)
    require(compressed[:2] == b"\x1f\x8b" and compressed[3] == 0 and compressed[4:8] == bytes(4), "gzip wrapper has metadata")
    require(gzip.decompress(compressed) == raw, "compressed cpio mismatch")
    files = newc_parse(raw)
    for name in ("init", "bin/sh", "dev", "proc", "sys", "run", "tmp"):
        require(name in files, f"required newc path missing: {name}")
    require((files["init"]["mode"] & 0o111) != 0 and digest(files["init"]["bytes"]) == INIT_SHA, "embedded /init mismatch")
    for name in ("dev", "proc", "sys", "run", "tmp"):
        require(files[name]["kind"] == 0o040000, f"{name} is not directory")
    for name in ("console", "null"):
        require(files["dev/" + name]["kind"] == 0o020000, f"dev/{name} not character device")
    return len(files)


def check_sha_list(folder):
    entries = (folder / "SHA256SUMS").read_text().splitlines()
    seen = set()
    for line in entries:
        require(re.fullmatch(r"[0-9a-f]{64}  \./[A-Za-z0-9_.-]+", line) is not None, "malformed SHA256SUMS entry")
        h, name = line.split("  ./", 1)
        require(name not in seen and name != "SHA256SUMS", "duplicate/self-referential SHA entry")
        seen.add(name)
        read_sha(folder / name, h)
    require(set(p.name for p in folder.iterdir() if p.is_file()) - {"SHA256SUMS"} == seen, "SHA256SUMS does not cover all evidence files")
    return len(seen)


def header_inputs(path):
    obj = json.loads(path.read_text())
    require(obj.get("schema") == "oneli-native-host-header-inputs-v1" and obj.get("purpose") == "structural-only" and obj.get("phone_boot_validated") is False, "header inputs not explicitly structural-only")
    for k, lim in (("os_version_raw", 32), ("kernel_addr", 32), ("ramdisk_addr", 32), ("tags_addr", 32), ("dtb_addr", 64)):
        n = obj.get(k)
        require(type(n) is int and 0 <= n < 2 ** lim, "missing/invalid explicit header field " + k)
    require(obj["os_version_raw"] == 0 and obj.get("signature_size") == 0 and obj.get("boot_cmdline") == obj.get("vendor_cmdline") == obj.get("bootconfig") == "", "host-only zero policy violated")
    d = obj.get("vendor_ramdisk_fragment") or {}
    require(d.get("type") == 1 and d.get("name") == "native-diag" and d.get("board_id") == [0] * 16, "unexpected vendor ramdisk fragment")
    return obj


def build(kernel, ramdisk, dtb, vendor, header):
    # boot header v4: 1584-byte AOSP layout and 4096-byte physical pages.
    b = bytearray(PAGE)
    b[0:8] = b"ANDROID!"
    struct.pack_into("<IIII", b, 8, len(kernel), len(ramdisk), header["os_version_raw"], 1584)
    struct.pack_into("<I", b, 40, 4)
    struct.pack_into("<I", b, 1580, 0)
    boot = bytes(b) + paged(kernel) + paged(ramdisk)
    # Explicit empty newc vendor platform fragment: valid AOSP table, no stock vendor files.
    v = bytearray(PAGE)
    v[0:8] = b"VNDRBOOT"
    struct.pack_into("<IIII", v, 8, 4, PAGE, header["kernel_addr"], header["ramdisk_addr"])
    struct.pack_into("<I", v, 24, len(vendor))
    struct.pack_into("<I", v, 2076, header["tags_addr"])
    v[2080:2080 + len(b"oneli")] = b"oneli"
    struct.pack_into("<II", v, 2096, 2128, len(dtb))
    struct.pack_into("<Q", v, 2104, header["dtb_addr"])
    struct.pack_into("<IIII", v, 2112, 108, 1, 108, 0)
    ent = struct.pack("<III32s16I", len(vendor), 0, 1, b"native-diag\0".ljust(32, b"\0"), *([0] * 16))
    require(len(ent) == 108, "vendor table entry wrong length")
    vendor_boot = bytes(v) + paged(vendor) + paged(dtb) + paged(ent)
    return boot, vendor_boot


def validate_structures(boot, vendor_boot, kernel, ramdisk, dtb, vendor, hdr):
    def u32(b, p): return struct.unpack_from("<I", b, p)[0]
    require(boot[:8] == b"ANDROID!" and len(boot) % PAGE == 0, "boot image magic/alignment")
    require(u32(boot, 20) == 1584 and u32(boot, 40) == 4, "boot v4 header conflict")
    require((u32(boot, 8), u32(boot, 12), u32(boot, 16), u32(boot, 1580)) == (len(kernel), len(ramdisk), 0, 0), "boot header sizes/signing")
    require(not any(boot[24:40]) and not any(boot[44:1580]), "boot reserved/cmdline not blank")
    for pos, data in ((PAGE, kernel), (PAGE + len(paged(kernel)), ramdisk)):
        require(boot[pos:pos + len(data)] == data, "boot payload structure mismatch")
    require(vendor_boot[:8] == b"VNDRBOOT" and len(vendor_boot) % PAGE == 0, "vendor image magic/alignment")
    require((u32(vendor_boot, 8), u32(vendor_boot, 12), u32(vendor_boot, 2096)) == (4, PAGE, 2128), "vendor v4 header")
    require((u32(vendor_boot, 24), u32(vendor_boot, 2100), u32(vendor_boot, 2112), u32(vendor_boot, 2116), u32(vendor_boot, 2120), u32(vendor_boot, 2124)) == (len(vendor), len(dtb), 108, 1, 108, 0), "vendor v4 header sizes")
    require((u32(vendor_boot, 16), u32(vendor_boot, 20), u32(vendor_boot, 2076), struct.unpack_from("<Q", vendor_boot, 2104)[0]) == (hdr["kernel_addr"], hdr["ramdisk_addr"], hdr["tags_addr"], hdr["dtb_addr"]), "vendor address mismatch")
    require(not any(vendor_boot[28:2076]), "vendor cmdline not blank")
    a, b, c = PAGE, PAGE + len(paged(vendor)), PAGE + len(paged(vendor)) + len(paged(dtb))
    require(vendor_boot[a:a + len(vendor)] == vendor and vendor_boot[b:b + len(dtb)] == dtb, "vendor sections mismatch")
    row = vendor_boot[c:c + 108]
    require(struct.unpack_from("<III", row) == (len(vendor), 0, 1) and row[12:44].split(b"\0")[0] == b"native-diag", "vendor fragment table mismatch")
    require(not any(row[44:108]), "vendor board IDs not zero")
    require(int.from_bytes(dtb[0:4], "big") == 0xd00dfeed and int.from_bytes(dtb[4:8], "big") == len(dtb), "mainline DTB truncated or non-FDT")
    return {"boot": {"sha256": digest(boot), "size": len(boot), "kernel_offset": PAGE, "kernel_sha256": digest(kernel), "ramdisk_offset": PAGE + len(paged(kernel)), "ramdisk_sha256": digest(ramdisk), "signature_size": 0, "os_version_raw": 0}, "vendor_boot": {"sha256": digest(vendor_boot), "size": len(vendor_boot), "fragment_type": 1, "fragment_name": "native-diag", "fragment_sha256": digest(vendor), "dtb_sha256": digest(dtb), "fragment_table_entries": 1, "bootconfig_size": 0}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kernel-dir", type=Path, required=True)
    ap.add_argument("--payload-dir", type=Path, required=True)
    ap.add_argument("--header-inputs", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    k, p = args.kernel_dir, args.payload_dir
    kernel = read_sha(k / "Image", IMAGE_SHA)
    config = read_sha(k / "kernel.config", CONFIG_SHA)
    dtb = read_sha(k / "sm8475-motorola-oneli.dtb", DTB_SHA)
    require((k / "kernel.release").read_text().strip() == RELEASE, "kernel release mismatch")
    expected_config = ["CONFIG_ARM64=y", "CONFIG_BLK_DEV_INITRD=y", "CONFIG_RD_GZIP=y", "CONFIG_BINFMT_SCRIPT=y", "CONFIG_PROC_FS=y", "CONFIG_SYSFS=y", "CONFIG_DEVTMPFS=y", "CONFIG_TMPFS=y", "CONFIG_SERIAL_QCOM_GENI=y", "CONFIG_SERIAL_QCOM_GENI_CONSOLE=y"]
    config_lines = set(config.decode().splitlines())
    require(all(s in config_lines for s in expected_config), "kernel configuration lacks required builtins")
    checks = check_sha_list(p)
    manifest = json.loads((p / "oneli-diag-payload-v1.json").read_text())
    members = ensure_ums_manifest(p, manifest)
    h = header_inputs(args.header_inputs)
    # Create the separately owned minimal platform vendor fragment, deliberately empty.
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "empty.cpio"
        src.write_bytes(newc_empty())
        pz = subprocess.run(["gzip", "-n", "-9", "-c", str(src)], capture_output=True, check=True)
    vendor = pz.stdout
    require(gzip.decompress(vendor) == newc_empty(), "empty vendor fragment construction failed")
    boot, vb = build(kernel, (p / "oneli-diag-initramfs.cpio.gz").read_bytes(), dtb, vendor, h)
    report = validate_structures(boot, vb, kernel, (p / "oneli-diag-initramfs.cpio.gz").read_bytes(), dtb, vendor, h)
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    (out / "boot-candidate.UNSIGNED.img").write_bytes(boot)
    (out / "vendor_boot-candidate.UNSIGNED.img").write_bytes(vb)
    (out / "vendor-platform-empty.cpio.gz").write_bytes(vendor)
    report.update({"schema": "oneli-native-host-validation-v1", "result": "structural-self-check-pass", "provenance": {"kernel_commit": KERNEL_COMMIT, "kernel_release": RELEASE, "user_payload_cpio_sha256": CPIO_SHA, "user_payload_gzip_sha256": GZIP_SHA, "user_payload_init_sha256": INIT_SHA, "user_payload_qemu_log_sha256": LOG_SHA, "user_sha256sums_count": checks, "newc_member_count": members}, "header_inputs": h, "native_flash_approved": False, "hardware_tested": False, "avb_signed": False, "independent_aosp_unpack": "pending-independent-test", "native_placement": "UNRESOLVED", "diagnostic_transport": "UNRESOLVED", "signature_policy": "zero boot-v4 signature; no AVB authentication"})
    (out / "native-host-validation.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"result": report["result"], "boot_sha256": report["boot"]["sha256"], "vendor_boot_sha256": report["vendor_boot"]["sha256"], "members": members}, sort_keys=True))


if __name__ == "__main__":
    main()
