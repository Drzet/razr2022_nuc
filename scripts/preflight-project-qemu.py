#!/usr/bin/env python3
"""Read Boot's immutable combined-build v1 ZIP *after safe extraction*, without root."""
import argparse
import gzip
import hashlib
import json
import lzma
import re
import shlex
import subprocess
import tempfile
from pathlib import Path

HASH = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
RELEASE = re.compile(r"[A-Za-z0-9._+~-]+\Z")
MODULES = (".ko", ".ko.gz", ".ko.xz", ".ko.zst")

def need(ok, why):
    if not ok:
        raise ValueError(why)

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def file_under(root, name):
    need(isinstance(name, str) and name and not name.startswith("/"),
         "relative artifact path required")
    p = (root / name).resolve(strict=True)
    need(p.is_relative_to(root) and p.is_file(), "artifact path escapes/absent: " + name)
    return p

def check_hash(root, name, expected):
    need(isinstance(expected, str) and HASH.fullmatch(expected), "unresolved SHA256: " + name)
    p = file_under(root, name)
    need(sha(p) == expected, "SHA256 mismatch: " + name)
    return p

def config_symbols(path):
    out = {}
    for line in path.read_text().splitlines():
        if re.fullmatch(r"CONFIG_[A-Za-z0-9_]+=[ymn]", line):
            key, value = line.split("=", 1)
            out[key] = value
        elif line.startswith("# CONFIG_") and line.endswith(" is not set"):
            out[line[2:-11]] = "n"
    return out

def module_vermagic(path):
    if path.name.endswith(".ko.gz"):
        b = gzip.decompress(path.read_bytes())
    elif path.name.endswith(".ko.xz"):
        b = lzma.decompress(path.read_bytes())
    elif path.name.endswith(".ko.zst"):
        b = subprocess.run(["zstd", "-dc", str(path)], check=True,
                           capture_output=True).stdout
    else:
        b = path.read_bytes()
    need(len(b) >= 20 and b[:4] == b"\x7fELF" and b[4] == 2 and
         b[5] == 1 and int.from_bytes(b[18:20], "little") == 183,
         "not AArch64 ELF module: " + path.name)
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "mod.ko"
        p.write_bytes(b)
        return subprocess.run(["modinfo", "-F", "vermagic", str(p)],
                              capture_output=True, text=True, check=True).stdout.strip()

def inspect(root):
    root = root.resolve(strict=True)
    need(root.is_dir(), "bundle root is not a directory")
    record = json.loads(file_under(root, "manifests/combined-kernel-build-v1.json").read_text())
    need(record.get("schema") == "oneli-combined-kernel-build-v1",
         "unsupported Boot wire manifest")
    need(record.get("repository") == "https://github.com/Drzet/linux",
         "wrong kernel repository")
    commit, release, build_id = (record.get(k) for k in
                                  ("kernel_commit", "kernel_release", "build_id"))
    need(isinstance(commit, str) and COMMIT.fullmatch(commit), "unknown combined kernel SHA")
    need(isinstance(release, str) and RELEASE.fullmatch(release), "unknown generated release")
    need(isinstance(build_id, str) and len(build_id.strip()) >= 8, "unknown build ID")
    files, hashes = record.get("files"), record.get("sha256")
    need(isinstance(files, dict) and isinstance(hashes, dict), "file list/hashes missing")
    spec = {"image": "boot/Image", "config": "boot/kernel.config",
            "module_symvers": "boot/Module.symvers", "kernel_release": "boot/kernel.release",
            "oneli_dtb": "boot/oneli.dtb",
            "modules_directory": "lib/modules/" + release}
    need(all(files.get(k) == v for k, v in spec.items()),
         "bundle paths differ from Boot/Userspace v1 wire layout")
    checked = {k: check_hash(root, files[k], hashes.get(k))
               for k in ("image", "config", "module_symvers", "kernel_release", "oneli_dtb")}
    need(checked["kernel_release"].read_text().strip() == release,
         "kernel.release payload differs from manifest and build")
    modules = (root / files["modules_directory"]).resolve(strict=True)
    need(modules.is_relative_to(root) and modules.is_dir() and modules.name == release,
         "wrong installed release tree")
    need(not any(p.is_symlink() for p in modules.rglob("*")),
         "installed modules contain build/source/dangling symlinks")
    need(sha(check_hash(root, files["modules_directory"] + "/modules.dep",
                        hashes.get("modules_dep"))) == hashes["modules_dep"],
         "bad modules.dep")
    module_files = sorted(p for p in modules.rglob("*")
                          if p.is_file() and p.name.endswith(MODULES))
    mod_hashes = record.get("modules_sha256")
    need(isinstance(mod_hashes, dict) and
         set(mod_hashes) == {p.relative_to(modules).as_posix() for p in module_files},
         "installed module hashes do not exhaustively match bundle")
    for p in module_files:
        rel = p.relative_to(modules).as_posix()
        need(sha(p) == mod_hashes[rel], "module hash mismatch: " + rel)
        actual = module_vermagic(p)
        need(actual and actual.split()[0] == release,
             "wrong-release module vermagic: " + rel)
    cfg = config_symbols(checked["config"])
    q = record.get("qemu_virt_config")
    need(isinstance(q, dict) and
         q.get("machine") == "virt" and q.get("console") == "ttyAMA0" and
         q.get("virtio_transport") == "mmio" and q.get("root_disk") == "virtio-blk" and
         q.get("network") == "virtio-net" and q.get("root_fs") == "ext4",
         "QEMU command/config profile mismatch")
    expected_builtin = ("CONFIG_ARM64", "CONFIG_SERIAL_AMBA_PL011",
        "CONFIG_SERIAL_AMBA_PL011_CONSOLE", "CONFIG_ARM_GIC", "CONFIG_VIRTIO_MMIO",
        "CONFIG_VIRTIO_BLK", "CONFIG_VIRTIO_NET", "CONFIG_EXT4_FS",
        "CONFIG_DEVTMPFS", "CONFIG_DEVTMPFS_MOUNT", "CONFIG_BLK_DEV_INITRD",
        "CONFIG_RD_GZIP", "CONFIG_INET", "CONFIG_UNIX", "CONFIG_PACKET",
        "CONFIG_TMPFS", "CONFIG_BINFMT_ELF")
    need(set(q.get("required_builtin", [])) >= set(expected_builtin),
         "Boot metadata omits mandatory QEMU built-in config checks")
    need(set(q.get("required_enabled", [])) >= {"CONFIG_MODULES"},
         "Boot metadata omits CONFIG_MODULES=y gate")
    need(set(q.get("required_loadable", [])) >= {"CONFIG_DUMMY"},
         "Boot metadata omits harmless loadable test module")
    for key in q["required_builtin"] + q["required_enabled"]:
        need(cfg.get(key) == "y", key + " is not built into the selected Image")
    for key in q["required_loadable"]:
        need(cfg.get(key) == "m", key + " must be an actual loadable module")
    chosen = record.get("qemu_runtime_module")
    need(isinstance(chosen, dict), "guest runtime module not selected")
    name, rel = chosen.get("name"), chosen.get("relative_path")
    need(isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9_-]+", name) and
         isinstance(rel, str) and rel in mod_hashes, "test module absent from installed tree")
    need(name == "dummy" and rel.startswith("kernel/drivers/net/dummy.ko"),
         "v1 contract requires dummy module; change spec before choosing another")
    toolchain = record.get("toolchain", {})
    need(all(isinstance(toolchain.get(k), str) and toolchain[k].strip()
             for k in ("compiler", "linker", "build_command")),
         "compiler/linker/command provenance incomplete")
    commits = record.get("commits")
    need(isinstance(commits, list) and commits and
         all(isinstance(x, dict) and isinstance(x.get("original"), str) and
             isinstance(x.get("applied"), str) and
             COMMIT.fullmatch(x["original"]) and COMMIT.fullmatch(x["applied"])
             for x in commits), "ordered original/result commit mapping missing")
    evidence = record.get("evidence", {})
    need(evidence.get("modpost_completed") is True and
         evidence.get("oneli_dtb_compiled") is True and
         evidence.get("phone_tested") is False, "build stage/test scope unsupported")
    return {"RELEASE": release, "MODULE": name, "IMAGE": str(checked["image"]),
            "CONFIG": str(checked["config"]), "MODDIR": str(modules),
            "COMMIT": commit, "BUILD_ID": build_id,
            "MODULE_SYMVERS": str(checked["module_symvers"]),
            "BUNDLE_MANIFEST": str(file_under(root, "manifests/combined-kernel-build-v1.json")),
            "BUNDLE": str(root)}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle-root", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    a = ap.parse_args()
    try:
        r = inspect(a.bundle_root)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as e:
        ap.exit(1, "PROJECT_QEMU_PREFLIGHT_FAILED: " + str(e) + "\n")
    if a.output:
        a.output.write_text("".join(k + "=" + shlex.quote(str(v)) + "\n" for k, v in r.items()))
    print("PROJECT_QEMU_PREFLIGHT_PASS release=" + r["RELEASE"] + " module=" + r["MODULE"])

if __name__ == "__main__":
    main()
