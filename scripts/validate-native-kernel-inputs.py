#!/usr/bin/env python3
"""Strict offline native artifacts gate, NOT Motorola or firmware runtime validation."""
import argparse
import hashlib
import json
import lzma
import gzip
import re
import subprocess
import tempfile
from pathlib import Path

FILES = ("image_path", "config_path", "dtb_path", "initramfs_path",
         "firmware_manifest_path", "boot_packaging_manifest_path")
DIRS = ("modules_directory", "firmware_directory")
HEX = re.compile(r"[0-9a-f]{64}\Z")
MOD_EXT = (".ko", ".ko.xz", ".ko.gz", ".ko.zst")

def require(ok, message):
    if not ok:
        raise ValueError(message)

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as fd:
        for data in iter(lambda: fd.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()

def checked_path(root, relative, kind="file"):
    require(isinstance(relative, str) and relative and not relative.startswith("/"), "relative path required")
    p = (root / relative).resolve(strict=True)
    require(p.is_relative_to(root), f"path escapes artifact root: {relative}")
    require(p.is_file() if kind == "file" else p.is_dir(), f"{relative} is not a {kind}")
    return p

def sha_match(path, expected, label):
    require(isinstance(expected, str) and HEX.fullmatch(expected), f"missing SHA256 for {label}")
    actual = digest(path)
    require(actual == expected, f"SHA256 mismatch for {label}")
    return actual

def module_raw(path):
    if path.name.endswith(".ko.xz"):
        return lzma.decompress(path.read_bytes())
    if path.name.endswith(".ko.gz"):
        return gzip.decompress(path.read_bytes())
    if path.name.endswith(".ko.zst"):
        return subprocess.run(["zstd", "-q", "-dc", str(path)], check=True, capture_output=True).stdout
    return path.read_bytes()

def vermagic_for(path, release):
    data = module_raw(path)
    require(len(data) >= 20 and data[:4] == b"\x7fELF", f"module is not ELF: {path.name}")
    require(data[4] == 2 and data[5] == 1 and int.from_bytes(data[18:20], "little") == 183,
            f"module is not AArch64 ELF: {path.name}")
    with tempfile.TemporaryDirectory() as directory:
        p = Path(directory) / "module.ko"
        p.write_bytes(data)
        v = subprocess.run(["modinfo", "-F", "vermagic", str(p)],
                           capture_output=True, text=True, check=True).stdout.strip()
    require(v and v.split()[0] == release, f"module vermagic mismatch: {path.name}: {v!r}")
    return v

def nonempty_list(v, label):
    require(isinstance(v, list) and len(v) > 0 and len(set(v)) == len(v), f"{label} must be unique nonempty list")
    require(all(isinstance(x, str) and x for x in v), f"{label} has invalid entries")
    return v

def validate(data, root):
    require(data.get("schema_version") == 2, "native input schema must be v2")
    require(data.get("repository") == "https://github.com/Drzet/linux", "incorrect kernel repository")
    require(re.fullmatch(r"[0-9a-f]{40}", str(data.get("kernel_commit", ""))), "unresolved kernel SHA")
    release = data.get("kernel_release")
    require(isinstance(release, str) and re.fullmatch(r"[A-Za-z0-9._+~-]+", release), "unresolved kernel release")
    declared = data.get("sha256")
    require(isinstance(declared, dict), "sha256 map must be supplied")
    paths = {k: checked_path(root, data.get(k)) for k in FILES}
    dirs = {k: checked_path(root, data.get(k), "directory") for k in DIRS}
    result = {"kernel_commit": data["kernel_commit"], "kernel_release": release, "inputs": {}}
    for k, p in paths.items():
        result["inputs"][k] = sha_match(p, declared.get(k), k)
    modules = dirs["modules_directory"]
    require(modules.name == release and modules.parent.name == "modules", "modules tree does not match kernel release")
    all_modules = sorted(p for p in modules.rglob("*") if p.is_file() and p.name.endswith(MOD_EXT))
    require(bool(all_modules), "no native kernel modules found")
    expected = data.get("modules_sha256")
    require(isinstance(expected, dict), "modules_sha256 map missing")
    rels = [p.relative_to(modules).as_posix() for p in all_modules]
    require(set(rels) == set(expected), "modules_sha256 must cover every kernel module, no extras")
    mod_output = {}
    for p, rel in zip(all_modules, rels):
        sha_match(p, expected[rel], rel)
        mod_output[rel] = vermagic_for(p, release)
    require((modules / "modules.dep").is_file(), "depmod modules.dep missing")
    require(checked_path(root, data.get("modules_directory") + "/modules.dep").is_file(), "modules.dep required")
    dep_sha = declared.get("modules_dep")
    sha_match(modules / "modules.dep", dep_sha, "modules.dep")
    required_modules = nonempty_list(data.get("initramfs_modules"), "initramfs_modules")
    require(set(required_modules).issubset(expected), "initramfs_modules must be identified native modules")
    cp = subprocess.run(["lsinitramfs", str(paths["initramfs_path"])],
                        capture_output=True, text=True, check=True)
    contents = set(line.removeprefix("./") for line in cp.stdout.splitlines())
    with tempfile.TemporaryDirectory() as expanded:
        subprocess.run(["unmkinitramfs", str(paths["initramfs_path"]), expanded],
                       check=True, capture_output=True)
        extracted = sorted(p for p in Path(expanded).rglob("*") if p.is_file())
        def embedded_file(suffix):
            matches = [p for p in extracted if p.as_posix().endswith("/" + suffix)]
            require(len(matches) == 1, "expected exactly one initramfs file: " + suffix)
            return matches[0]
        for rel in required_modules:
            suffix = "lib/modules/" + release + "/" + rel
            require(any(x == suffix or x.endswith("/" + suffix) for x in contents),
                    f"required module missing from initramfs listing: {rel}")
            embedded = embedded_file(suffix)
            sha_match(embedded, expected[rel], "initramfs module " + rel)
            require(vermagic_for(embedded, release) == mod_output[rel],
                    "initramfs module vermagic disagreement: " + rel)
        fw_manifest = json.loads(paths["firmware_manifest_path"].read_text())
        require(fw_manifest.get("schema_version") == 1 and fw_manifest.get("status") == "complete",
                "firmware requirements unresolved; refuse empty or incomplete manifest")
        fw_entries = fw_manifest.get("required_files")
        require(isinstance(fw_entries, list) and fw_entries, "firmware manifest must identify required files")
        require(fw_manifest.get("unknown_requirements") == [], "unknown firmware requirements remain unresolved")
        fw_output = {}
        for row in fw_entries:
            require(isinstance(row, dict), "invalid firmware record")
            name, sha, consumer = row.get("path"), row.get("sha256"), row.get("consumer")
            require(isinstance(name, str) and name and isinstance(consumer, str) and consumer,
                    "firmware path and consumer required")
            path = checked_path(dirs["firmware_directory"], name)
            fw_output[name] = sha_match(path, sha, "firmware " + name)
            require(isinstance(row.get("in_initramfs"), bool), "firmware initramfs requirement must be explicit")
            if row["in_initramfs"]:
                suffix = "lib/firmware/" + name
                require(any(x == suffix or x.endswith("/" + suffix) for x in contents),
                        f"required firmware missing from initramfs listing: {name}")
                sha_match(embedded_file(suffix), sha, "initramfs firmware " + name)

    package_manifest = json.loads(paths["boot_packaging_manifest_path"].read_text())
    require(package_manifest.get("status") == "verified", "boot packaging remains unresolved")
    result["module_count"] = len(all_modules)
    result["module_vermagic"] = mod_output
    result["firmware_sha256"] = fw_output
    result["initramfs_checked_modules"] = required_modules
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text())
        result = validate(data, args.artifact_root.resolve(strict=True))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as e:
        parser.exit(1, f"NATIVE_ARTIFACT_GATE_FAILED: {e}\n")
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"NATIVE_ARTIFACT_STATIC_PASS {result['kernel_release']} modules={result['module_count']}")
    print("Only offline module, file, firmware-record and initramfs consistency; no phone validation.")

if __name__ == "__main__":
    main()
