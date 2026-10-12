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

FILES = ("image_path", "config_path", "module_symvers_path", "initramfs_path",
         "firmware_manifest_path")
DIRS = ("modules_directory",)
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

def scoped_list(v, label, reason):
    require(isinstance(v, list) and len(set(v)) == len(v), f"{label} must contain unique names")
    require(all(isinstance(x, str) and x for x in v), f"{label} invalid name")
    if not v:
        require(isinstance(reason, str) and len(reason.strip()) >= 20,
                f"{label} empty without explicit scoped justification")
    return v

def parse_firmware(d, target):
    require(d.get("schema_version") == 2 and d.get("target_environment") == target,
            "firmware manifest scope or version unresolved")
    require(d.get("assessment") == "complete" and d.get("unknown_requirements") == [],
            "firmware requirements unresolved")
    rows = d.get("required_files")
    require(isinstance(rows, list), "required_files must be an array")
    if not rows:
        require(isinstance(d.get("zero_requirements_reason"), str) and
                len(d["zero_requirements_reason"].strip()) >= 20,
                "empty firmware requirements need scope justification")
    return rows

def inspect_boot_packaging(d):
    # Structural reference evidence MUST NOT be promoted to native/physical readiness.
    require(d.get("schema") == "oneli-native-boot-packaging-contract-v2",
            "Boot v2 reference contract required; generic status=verified not supported")
    v = d.get("reference_images", {}).get("vendor_boot", {})
    b = d.get("reference_images", {}).get("boot", {})
    require(v.get("header_version") == 4 and v.get("header_bytes") == 2128 and
            v.get("page_bytes") == 4096 and b.get("header_version") == 4 and
            b.get("header_bytes") == 1584, "mismatched stock header metadata")
    require(v.get("ramdisk_table_entries") == 1 and v.get("ramdisk_table_entry_bytes") == 108 and
            v.get("ramdisk_fragment_type") == 1 and
            v.get("ramdisk_fragment_board_id_words") == [0] * 16,
            "stock fragment descriptor differs from published reference")
    proto = d.get("prototype", {})
    require(proto.get("flash_recipe") is False and proto.get("candidate_signed") is False and
            proto.get("boot_tested") is False and proto.get("native_ready") is False and
            proto.get("hardware_accepted") is False,
            "reference stage must not claim boot success")
    require(proto.get("implicit_reference_placement_inheritance") is False and
            proto.get("header_inputs_require_explicit_os_version") is True and
            proto.get("header_inputs_fields") ==
            ["os_version_raw", "kernel_addr", "ramdisk_addr", "tags_addr",
             "dtb_addr", "purpose", "phone_boot_validated"] and
            "header-inputs" in proto.get("requires_explicit_payload_paths", []),
            "Boot v2 must require explicit candidate header inputs")
    require(all(v.get(k) is not None for k in
                ("kernel_addr", "ramdisk_addr", "tags_addr", "dtb_addr")),
            "missing observed stock reference load addresses (not native approval)")
    require(v.get("embedded_dtb_count") == 2 and
            [p.get("relative_offset") for p in v.get("embedded_dtb_roots", [])] ==
            [0, 479481], "reference embedded base FDT layout unresolved")
    return {"structural_reference_audited": True, "native_composition_ready": False,
            "hardware_accepted": False, "boot_os_version_unresolved": b.get("os_version_raw") is None,
            "reference_addresses": {k: v.get(k) for k in
                                    ("kernel_addr", "ramdisk_addr", "tags_addr", "dtb_addr")}}

def inspect_native_header_inputs(d):
    fields = ("os_version_raw", "kernel_addr", "ramdisk_addr", "tags_addr", "dtb_addr")
    require(isinstance(d, dict), "native header inputs must be explicit JSON")
    require(d.get("purpose") in ("structural-only", "reviewed-native"),
            "unsupported native header purpose")
    for key in fields:
        value, bits = d.get(key), (64 if key == "dtb_addr" else 32)
        require(type(value) is int and 0 <= value < (1 << bits),
                f"native header {key} requires explicit unsigned {bits}-bit integer")
    require(d.get("phone_boot_validated") is False,
            "native header must not claim handset validation")
    return {"purpose": d["purpose"], "native_load_addresses_approved": False,
            "hardware_accepted": False}

def same_build(data, sha):
    b = data.get("same_build")
    require(isinstance(b, dict), "immutable same_build provenance required")
    require(b.get("kernel_commit") == data["kernel_commit"] and
            b.get("kernel_release") == data["kernel_release"], "commit/release build mismatch")
    require(b.get("config_sha256") == sha.get("config_path") and
            b.get("module_symvers_sha256") == sha.get("module_symvers_path") and
            b.get("image_sha256") == sha.get("image_path"),
            "Image/config/Module.symvers must share source build provenance")
    require(isinstance(b.get("build_id"), str) and len(b["build_id"]) >= 8,
            "combined build ID required")
    return b

def validate(data, root):
    require(data.get("schema_version") == 3, "native input schema must be v3")
    target = data.get("target_environment")
    require(target in ("qemu_virt", "oneli_native"), "unknown target environment")
    require(data.get("repository") == "https://github.com/Drzet/linux", "incorrect kernel repository")
    require(re.fullmatch(r"[0-9a-f]{40}", str(data.get("kernel_commit", ""))), "unresolved kernel SHA")
    release = data.get("kernel_release")
    require(isinstance(release, str) and re.fullmatch(r"[A-Za-z0-9._+~-]+", release), "unresolved kernel release")
    declared = data.get("sha256")
    require(isinstance(declared, dict), "sha256 map must be supplied")
    paths = {k: checked_path(root, data.get(k)) for k in FILES}
    if target == "oneli_native":
        for name in ("dtb_path", "boot_packaging_manifest_path", "native_header_inputs_path"):
            paths[name] = checked_path(root, data.get(name))
    else:
        require(data.get("dtb_path") is None and
                data.get("boot_packaging_manifest_path") is None and
                data.get("native_header_inputs_path") is None,
                "QEMU virt must use its own DT; oneli packaging forbidden")
    dirs = {k: checked_path(root, data.get(k), "directory") for k in DIRS}
    result = {"kernel_commit": data["kernel_commit"], "kernel_release": release, "inputs": {}}
    for k, p in paths.items():
        result["inputs"][k] = sha_match(p, declared.get(k), k)
    result["same_build"] = same_build(data, declared)
    result["target_environment"] = target
    if target == "oneli_native":
        result["native_header_inputs"] = inspect_native_header_inputs(
            json.loads(paths["native_header_inputs_path"].read_text()))
    result["packaging"] = (inspect_boot_packaging(json.loads(paths["boot_packaging_manifest_path"].read_text()))
                           if target == "oneli_native" else
                           {"not_applicable": True, "native_composition_ready": False,
                            "hardware_accepted": False})
    modules = dirs["modules_directory"]
    require(modules.name == release and modules.parent.name == "modules", "modules tree does not match kernel release")
    all_modules = sorted(p for p in modules.rglob("*") if p.is_file() and p.name.endswith(MOD_EXT))
    if not all_modules:
        require("CONFIG_MODULES=n" in paths["config_path"].read_text().splitlines(),
                "empty modules require an explicit CONFIG_MODULES=n kernel")
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
    required_modules = scoped_list(data.get("initramfs_modules"), "initramfs_modules",
                                   data.get("zero_initramfs_modules_reason"))
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
        fw_entries = parse_firmware(fw_manifest, target)
        if fw_entries:
            firmware_root = checked_path(root, data.get("firmware_directory"), "directory")
        else:
            require(data.get("firmware_directory") is None,
                    "empty firmware profile must not carry a stray firmware directory")
            firmware_root = None
        fw_output = {}
        for row in fw_entries:
            require(isinstance(row, dict), "invalid firmware record")
            name, sha, consumer = row.get("path"), row.get("sha256"), row.get("consumer")
            require(isinstance(name, str) and name and isinstance(consumer, str) and consumer,
                    "firmware path and consumer required")
            path = checked_path(firmware_root, name)
            fw_output[name] = sha_match(path, sha, "firmware " + name)
            require(isinstance(row.get("in_initramfs"), bool), "firmware initramfs requirement must be explicit")
            if row["in_initramfs"]:
                suffix = "lib/firmware/" + name
                require(any(x == suffix or x.endswith("/" + suffix) for x in contents),
                        f"required firmware missing from initramfs listing: {name}")
                sha_match(embedded_file(suffix), sha, "initramfs firmware " + name)

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
