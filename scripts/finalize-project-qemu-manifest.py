#!/usr/bin/env python3
"""Finalize Userspace schema v3 *after* generating project-matching initramfs."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

def digest(p):
    h = hashlib.sha256()
    with p.open("rb") as fd:
        for b in iter(lambda: fd.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle-root", type=Path, required=True)
    ap.add_argument("--initramfs", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    a = ap.parse_args()
    manifest = json.loads((a.bundle_root / "manifests/combined-kernel-build-v1.json").read_text())
    assert manifest["schema"] == "oneli-combined-kernel-build-v1"
    assert not a.output_root.exists(), "refuse to reuse output-root"
    a.output_root.mkdir(parents=True)
    paths = {
        "image_path": "boot/Image",
        "config_path": "boot/kernel.config",
        "module_symvers_path": "boot/Module.symvers",
        "initramfs_path": "boot/initrd.img",
        "firmware_manifest_path": "manifests/qemu-virt-firmware-v2.json",
    }
    for key, source in (("image_path", "image"), ("config_path", "config"),
                        ("module_symvers_path", "module_symvers")):
        dst = a.output_root / paths[key]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(a.bundle_root / manifest["files"][source], dst)
    init = a.output_root / paths["initramfs_path"]
    shutil.copy2(a.initramfs, init)
    fw = {
        "schema_version": 2, "target_environment": "qemu_virt",
        "assessment": "complete", "unknown_requirements": [],
        "required_files": [],
        "zero_requirements_reason": (
            "Selected virt ARM64 config builds PL011, virtio MMIO, block, network and "
            "ext4 into the kernel, with no active proprietary firmware consumers")
    }
    fwp = a.output_root / paths["firmware_manifest_path"]
    fwp.parent.mkdir(parents=True, exist_ok=True)
    fwp.write_text(json.dumps(fw, sort_keys=True, indent=2) + "\n")
    modules = manifest["files"]["modules_directory"]
    shutil.copytree(a.bundle_root / modules, a.output_root / modules,
                    symlinks=False)
    release, commit = manifest["kernel_release"], manifest["kernel_commit"]
    full = {
        "schema_version": 3, "repository": "https://github.com/Drzet/linux",
        "target_environment": "qemu_virt", "kernel_commit": commit,
        "kernel_release": release,
        **paths,
        "dtb_path": None, "boot_packaging_manifest_path": None,
        "native_header_inputs_path": None,
        "modules_directory": modules, "firmware_directory": None,
        "initramfs_modules": [],
        "zero_initramfs_modules_reason": (
            "Verified QEMU serial, interrupt, root virtio-blk, network and ext4 "
            "requirements are built in; no early loadable driver selected"),
        "qemu_runtime_module": manifest["qemu_runtime_module"],
        "modules_sha256": manifest["modules_sha256"],
        "same_build": {
            "kernel_commit": commit, "kernel_release": release,
            "build_id": manifest["build_id"],
            "image_sha256": manifest["sha256"]["image"],
            "config_sha256": manifest["sha256"]["config"],
            "module_symvers_sha256": manifest["sha256"]["module_symvers"]},
        "sha256": {k: digest(a.output_root / v) for k, v in paths.items()}
    }
    full["sha256"]["modules_dep"] = digest(a.output_root / modules / "modules.dep")
    (a.output_root / "native-inputs-v3.json").write_text(
        json.dumps(full, indent=2, sort_keys=True) + "\n")
    print("PROJECT_QEMU_V3_MANIFEST_STAGED release=" + release)

if __name__ == "__main__":
    main()
