#!/usr/bin/env python3
"""Offline input gate. A passing result is NOT an oneli boot or firmware validation."""
import argparse
import hashlib
import json
import re
from pathlib import Path

KEYS = ("kernel_commit", "kernel_release", "image_path", "config_path",
        "dtb_path", "modules_directory", "initramfs_path",
        "firmware_manifest_path", "firmware_directory", "boot_packaging_manifest_path")

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--artifact-root", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    d = json.loads(args.manifest.read_text())
    if d.get("schema_version") != 1 or d.get("repository") != "https://github.com/Drzet/linux":
        raise SystemExit("Unexpected input schema or repository")
    missing = [k for k in KEYS if not isinstance(d.get(k), str) or not d[k]]
    if missing:
        raise SystemExit("Native artifact gate deferred; missing: " + ", ".join(missing))
    if not re.fullmatch(r"[0-9a-f]{40}", d["kernel_commit"]):
        raise SystemExit("kernel_commit must be an exact 40-digit SHA")
    release = d["kernel_release"]
    if not re.fullmatch(r"[A-Za-z0-9._+~-]+", release):
        raise SystemExit("Invalid native kernel release")
    root = args.artifact_root.resolve(strict=True)
    result = {"kernel_commit": d["kernel_commit"], "kernel_release": release, "files": {}}
    for key in KEYS[2:]:
        p = (root / d[key]).resolve(strict=True)
        if not p.is_relative_to(root):
            raise SystemExit(f"Path escapes artifact root: {key}")
        if key in ("modules_directory", "firmware_directory"):
            if not p.is_dir():
                raise SystemExit(f"{key} is not a directory")
            result["files"][key] = {"path": str(p.relative_to(root)), "type": "directory"}
        else:
            if not p.is_file():
                raise SystemExit(f"{key} is not a file")
            result["files"][key] = {"path": str(p.relative_to(root)), "sha256": sha256(p)}
    modules = (root / d["modules_directory"]).resolve()
    if modules.name != release or modules.parent.name != "modules":
        raise SystemExit("Modules must be installed under lib/modules/<native kernel_release>")
    if not (modules / "modules.dep").is_file():
        raise SystemExit("Missing depmod-generated modules.dep")
    if not any(modules.rglob("*.ko*")):
        raise SystemExit("No kernel modules found under matching release")
    if not isinstance(json.loads((root / d["firmware_manifest_path"]).read_text()), dict):
        raise SystemExit("Firmware manifest must be a JSON object")
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("NATIVE_ARTIFACT_STATIC_PASS " + release)
    print("This only checks local artifact consistency; it is not oneli validation.")

if __name__ == "__main__":
    main()
