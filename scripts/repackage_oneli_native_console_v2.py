#!/usr/bin/env python3
"""One host-only v2 ramdisk update; preserve the accepted v1 vendor_boot bytes.

Reuse the exact frozen Boot v1 verifier/packer, but bind its four Userspace
digests to independently verified v2 artifact hashes. Never mutate partitions.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
BASE = HERE / "build_oneli_native_host_candidate.py"
BASE_BLOB_SHA1 = "8221b23255489f7e94d3b267106c36db02c31df5"
PROBE_FIXTURE = "RAZR_NATIVE_PROBE_ERROR_FIXTURE_CI_ONLY"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pinned_base():
    b = BASE.read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    need(git_blob == BASE_BLOB_SHA1, "base v1 packer changed; review before v2 repack")
    spec = importlib.util.spec_from_file_location("oneli_host_v1", BASE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def console_fixture(data):
    rows = data.decode("utf-8", "replace").splitlines()
    begin = [i for i, s in enumerate(rows) if s.strip() == "RAZR_NATIVE_DIAG_PROBE_ERRORS_BEGIN"]
    end = [i for i, s in enumerate(rows) if s.strip() == "RAZR_NATIVE_DIAG_PROBE_ERRORS_END"]
    need(len(begin) == len(end) == 1 and begin[0] < end[0], "missing/reordered probe marker lines")
    selection = rows[begin[0] + 1:end[0]]
    need(selection and len(selection) <= 80, "empty or unbounded probe summary")
    need(sum(len(x.encode("utf-8")) + 1 for x in selection) <= 16384 + 80, "summary exceeds byte bound")
    need(any(PROBE_FIXTURE in row for row in selection), "fixture absent between console markers")
    return len(selection)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kernel-dir", required=True, type=Path)
    p.add_argument("--payload-dir", required=True, type=Path)
    p.add_argument("--header-inputs", required=True, type=Path)
    p.add_argument("--vendor-boot-v1", required=True, type=Path)
    p.add_argument("--input-lock", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()

    lock = json.loads(args.input_lock.read_text())
    need(lock["schema"] == "oneli-native-host-console-v2-input-lock", "bad input lock schema")
    need(lock["purpose"] == "repackage-only-changed-generic-diagnostic-ramdisk; no new kernel or vendor_boot", "bad purpose")
    need(lock["safety"] == {
        "phone_boot_validated": False, "native_flash_approved": False,
        "AVB_signed": False, "host_only": True
    }, "lock does not prohibit hardware use")
    v2 = lock["userspace_v2"]
    need(v2["payload_revision"] == "console-summary-v2" and
         v2["interface"] == "oneli-native-early-initramfs-interface-v1" and
         v2["console_fixture"] == PROBE_FIXTURE, "bad Userspace release identity")
    need(v2["source_commit"] == "64b7a3358d3250dbe92518e548517ddfd038b149" and
         v2["artifact_id"] == 11777077254 and v2["run_id"] == 38317559417,
         "unexpected untested Userspace source/artifact")
    need(lock["pinned_boot_code"]["git_blob_sha1"] == BASE_BLOB_SHA1, "unexpected base packer revision")
    need(lock["immutable_vendor_boot_v1"]["vendor_boot_sha256"] ==
         "1b4f6379b41e22735176bf63c725d3455d47c7b510f29d0de62b408da5f47572",
         "unexpected accepted v1 vendor_boot")

    base = pinned_base()
    base.CPIO_SHA = v2["cpio_sha256"]
    base.GZIP_SHA = v2["compressed_sha256"]
    base.INIT_SHA = v2["init_sha256"]
    base.LOG_SHA = v2["qemu_positive_log_sha256"]

    kernel_lock = lock["frozen_kernel"]
    for name, expected in (
        ("Image",kernel_lock["Image_sha256"]),
        ("kernel.config",kernel_lock["config_sha256"]),
        ("sm8475-motorola-oneli.dtb",kernel_lock["dtb_sha256"]),
    ):
        need(base.digest((args.kernel_dir / name).read_bytes()) == expected, f"kernel input {name} digest mismatch")
    need((args.kernel_dir / "kernel.release").read_text().strip() == kernel_lock["release"],
         "kernel release mismatch")
    config = set((args.kernel_dir / "kernel.config").read_text().splitlines())
    require_builtins = (
        "CONFIG_ARM64=y", "CONFIG_BLK_DEV_INITRD=y", "CONFIG_RD_GZIP=y",
        "CONFIG_BINFMT_SCRIPT=y", "CONFIG_PROC_FS=y", "CONFIG_SYSFS=y",
        "CONFIG_DEVTMPFS=y", "CONFIG_TMPFS=y", "CONFIG_SERIAL_QCOM_GENI=y",
        "CONFIG_SERIAL_QCOM_GENI_CONSOLE=y"
    )
    need(all(x in config for x in require_builtins), "missing accepted builtin required for diagnostic")
    count = base.check_sha_list(args.payload_dir)

    manifest = json.loads((args.payload_dir / "oneli-diag-payload-v1.json").read_text())
    need(manifest.get("payload_revision") == "console-summary-v2", "v1 payload falsely used as v2")
    need(manifest.get("qemu_validation", {}).get("console_probe_fixture_verified") is True,
         "QEMU fixture missing from typed manifest")
    need(manifest["qemu_validation"].get("console_probe_fixture") == PROBE_FIXTURE,
         "QEMU fixture identifier mismatch")
    need(manifest["qemu_validation"].get("hold_serial_log_sha256") ==
         v2["qemu_hold_log_sha256"], "hold log digest contract mismatch")
    member_count = base.ensure_ums_manifest(args.payload_dir, manifest)
    hold_name = base.check_simple(manifest["qemu_validation"]["hold_serial_log_relative_path"])
    need(hold_name == "qemu-hold-serial.log", "unexpected hold filename")
    hold = base.read_sha(args.payload_dir / hold_name, v2["qemu_hold_log_sha256"])
    positive = base.read_sha(args.payload_dir / "qemu-serial.log", v2["qemu_positive_log_sha256"])
    pos_lines, hold_lines = console_fixture(positive), console_fixture(hold)
    need(b"RAZR_NATIVE_DIAG_HOLD" in hold and b"RAZR_NATIVE_DIAG_READY_V1" in hold, "hold mode missing")
    need(b"RAZR_NATIVE_DIAG_QEMU_SHUTDOWN" not in hold, "hold unexpectedly powered off")

    header = base.header_inputs(args.header_inputs)
    need(header["os_version_raw"] == 0 and
         header.get("purpose") == "structural-only" and
         header.get("phone_boot_validated") is False, "native header gate violated")
    kernel = (args.kernel_dir / "Image").read_bytes()
    ramdisk = (args.payload_dir / "oneli-diag-initramfs.cpio.gz").read_bytes()
    dtb = (args.kernel_dir / "sm8475-motorola-oneli.dtb").read_bytes()
    with tempfile.TemporaryDirectory() as td:
        empty = Path(td) / "empty.cpio"
        empty.write_bytes(base.newc_empty())
        vendor = subprocess.run(
            ["gzip","-n","-9","-c",str(empty)],
            stdout=subprocess.PIPE,check=True
        ).stdout
    need(gzip.decompress(vendor) == base.newc_empty(), "vendor platform fragment not empty deterministic newc")
    boot, unchanged_vendor = base.build(kernel, ramdisk, dtb, vendor, header)
    report = base.validate_structures(boot, unchanged_vendor, kernel, ramdisk, dtb, vendor, header)
    v1_vendor = base.read_sha(args.vendor_boot_v1, lock["immutable_vendor_boot_v1"]["vendor_boot_sha256"])
    need(unchanged_vendor == v1_vendor, "v2 attempts to change accepted v1 vendor_boot")

    need(not args.output.exists(), "output must be new directory")
    args.output.mkdir(parents=True)
    (args.output / "boot-console-v2.UNSIGNED.img").write_bytes(boot)
    output = {
      "schema":"oneli-native-host-console-v2-validation",
      "result":"self-inspection-pass-aosp-independent-pending",
      "kernel_commit":kernel_lock["commit"],
      "kernel_release":kernel_lock["release"],
      "userspace_v2":v2,
      "v1_vendor_boot_reused":{
        "source_artifact_id":lock["immutable_vendor_boot_v1"]["artifact_id"],
        "sha256":digest(v1_vendor),
        "new_vendor_image_published":False
      },
      "host_structural_boot_v4":report["boot"],
      "reference_vendor_boot_v4":report["vendor_boot"],
      "v2_console_probe_summary":{
        "positive_lines":pos_lines,
        "hold_lines":hold_lines,
        "fixture":PROBE_FIXTURE,
        "positive_log_sha256":digest(positive),
        "hold_log_sha256":digest(hold)
      },
      "archive_sha256sums_verified":count,
      "newc_members_verified":member_count,
      "native_flash_approved":False,
      "hardware_tested":False,
      "avb_signed":False,
      "physical_diagnostic_route":"UNRESOLVED",
      "loader_memory_placement":"UNRESOLVED",
      "native_dtbo_selection":"UNRESOLVED"
    }
    (args.output / "boot-console-v2-inspection.json").write_text(
        json.dumps(output,sort_keys=True,indent=2) + "\n"
    )
    print(json.dumps({"status":output["result"],"boot_sha256":digest(boot),
                      "vendor_boot_unchanged_sha256":digest(v1_vendor),
                      "positive_probe_lines":pos_lines,"hold_probe_lines":hold_lines},sort_keys=True))


if __name__ == "__main__":
    main()
