#!/usr/bin/env python3
"""Verify Boot's actual portable artifact v1, then adapt into Userspace's staging tree."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

BUILTINS = ["CONFIG_ARM64","CONFIG_SERIAL_AMBA_PL011","CONFIG_SERIAL_AMBA_PL011_CONSOLE",
 "CONFIG_ARM_GIC","CONFIG_VIRTIO_MMIO","CONFIG_VIRTIO_BLK","CONFIG_VIRTIO_NET",
 "CONFIG_EXT4_FS","CONFIG_DEVTMPFS","CONFIG_DEVTMPFS_MOUNT","CONFIG_BLK_DEV_INITRD",
 "CONFIG_RD_GZIP","CONFIG_INET","CONFIG_UNIX","CONFIG_PACKET","CONFIG_TMPFS","CONFIG_BINFMT_ELF"]
MODULE_EXT=(".ko",".ko.gz",".ko.xz",".ko.zst")
def need(ok,why):
    if not ok: raise ValueError(why)
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""): h.update(block)
    return h.hexdigest()
def secure(root,path):
    need(isinstance(path,str) and path and not Path(path).is_absolute() and
         ".." not in Path(path).parts,"unsafe bundle path")
    p=root/path
    need(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(root),
         "missing or unsafe Boot artifact: "+path)
    return p
def inspect(root):
    root=root.resolve(strict=True)
    need(root.is_dir(),"Boot root must be a directory")
    sums={}
    for ln in secure(root,"SHA256SUMS").read_text().splitlines():
        bits=ln.split("  ",1)
        need(len(bits)==2 and re.fullmatch("[0-9a-f]{64}",bits[0]) and
             bits[1] not in sums,"bad checksum record")
        sums[bits[1].removeprefix("./")]=bits[0]
    for p,h in sums.items():
        need(sha(secure(root,p))==h,"Boot SHA256SUMS mismatch: "+p)
    b=json.loads(secure(root,"build-manifest.json").read_text())
    v=json.loads(secure(root,"qemu-native-inputs.v3.preflight.json").read_text())
    inv=json.loads(secure(root,"module-sha256.json").read_text())
    fw=json.loads(secure(root,"firmware-qemu-virt.json").read_text())
    need(b.get("schema")=="oneli-combined-build-manifest-v1" and
         v.get("schema_version")==3 and v.get("target_environment")=="qemu_virt",
         "Boot artifact producer schemas mismatch")
    release,commit,build=b.get("kernel_release"),b.get("kernel_commit"),b.get("build_id")
    need(isinstance(release,str) and re.fullmatch("[A-Za-z0-9._+~-]+",release),
         "kernel release invalid")
    need(isinstance(commit,str) and re.fullmatch("[0-9a-f]{40}",commit) and
         isinstance(build,str) and len(build)>=8,"source SHA/build identity absent")
    need(v.get("kernel_commit")==commit and v.get("kernel_release")==release and
         v.get("same_build",{}).get("build_id")==build,
         "Boot producer preflight and build provenance mismatch")
    need(v.get("dtb_path") is None and v.get("boot_packaging_manifest_path") is None and
         v.get("initramfs_path") is None and v.get("sha256",{}).get("initramfs_path") is None,
         "Boot incorrectly supplies phone DT or nonexistent initramfs for QEMU")
    for name,key in (("Image","image_path"),("kernel.config","config_path"),
                     ("Module.symvers","module_symvers_path")):
        h=sha(secure(root,name))
        need(v.get(key)==name and b.get("files_sha256",{}).get(name)==h and
             v.get("sha256",{}).get(key)==h,"producer file hash mismatch: "+name)
    for name in ("kernel.release","sm8475-motorola-oneli.dtb"):
        need(sha(secure(root,name))==b.get("files_sha256",{}).get(name),
             "producer release/DTB SHA mismatch")
    need(secure(root,"kernel.release").read_text().strip()==release and
         sha(secure(root,".config"))==sha(secure(root,"kernel.config")),
         "generated config or kernel.release disagreement")
    modpath="modules/"+release
    moddir=root/modpath
    need(b.get("module_tree")==v.get("modules_directory")==modpath and moddir.is_dir(),
         "modules tree mismatch")
    need(not any(p.is_symlink() for p in moddir.rglob("*")),
         "Boot modules archive contains links")
    mods={p.relative_to(moddir).as_posix():sha(p) for p in moddir.rglob("*")
          if p.is_file() and p.name.endswith(MODULE_EXT)}
    need(bool(mods) and mods==inv==v.get("modules_sha256") and
         len(mods)==b.get("module_count"),"module hash list is not exhaustive")
    need(sha(secure(root,modpath+"/modules.dep"))==b.get("modules_dep_sha256")==
         v.get("sha256",{}).get("modules_dep"),"depmod inventory mismatch")
    need(v.get("qemu_runtime_module")=={"name":"dummy",
         "relative_path":"kernel/drivers/net/dummy.ko"} and
         "kernel/drivers/net/dummy.ko" in mods,"missing selected dummy modprobe module")
    need(v.get("firmware_manifest_path")=="firmware-qemu-virt.json" and
         v.get("sha256",{}).get("firmware_manifest_path")==sha(root/"firmware-qemu-virt.json"),
         "Boot firmware record digest disagrees")
    need(fw.get("schema_version")==2 and fw.get("target_environment")=="qemu_virt" and
         fw.get("assessment")=="complete" and fw.get("unknown_requirements")==[] and
         fw.get("required_files")==[] and len(fw.get("zero_requirements_reason",""))>=20,
         "unresolved or unexpected QEMU firmware requirements")
    need(b.get("qemu_runtime_module")=="dummy" and
         b.get("source_config_project_commit")=="6a80ab302e9e2cf5aaf3ca0187baec106e985ade",
         "Boot config source pin changed")
    mapping=b.get("replayed_commits")
    need(isinstance(mapping,list) and len(mapping)==7 and all(
         re.fullmatch("[0-9a-f]{40}",x.get("original","")) and
         re.fullmatch("[0-9a-f]{40}",x.get("result","")) for x in mapping),
         "ordered combined source commits absent")
    need(secure(root,"logs/toolchain.txt").stat().st_size>0,
         "Boot toolchain provenance missing")
    return root,b,v,mods
def convert(root,out):
    root,b,v,mods=inspect(root)
    need(not out.exists(),"refuse existing normalized bundle")
    release=b["kernel_release"]
    names={"Image":"boot/Image","kernel.config":"boot/kernel.config",
           "Module.symvers":"boot/Module.symvers","kernel.release":"boot/kernel.release",
           "sm8475-motorola-oneli.dtb":"boot/oneli.dtb"}
    out.mkdir(parents=True)
    for old,new in names.items():
        p=out/new
        p.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(root/old,p)
    shutil.copytree(root/("modules/"+release),out/("lib/modules/"+release))
    manifest={
      "schema":"oneli-combined-kernel-build-v1",
      "repository":"https://github.com/Drzet/linux",
      "kernel_commit":b["kernel_commit"],"kernel_release":release,"build_id":b["build_id"],
      "files":{"image":"boot/Image","config":"boot/kernel.config",
               "module_symvers":"boot/Module.symvers","kernel_release":"boot/kernel.release",
               "oneli_dtb":"boot/oneli.dtb","modules_directory":"lib/modules/"+release},
      "sha256":{"image":b["files_sha256"]["Image"],
                "config":b["files_sha256"]["kernel.config"],
                "module_symvers":b["files_sha256"]["Module.symvers"],
                "kernel_release":b["files_sha256"]["kernel.release"],
                "oneli_dtb":b["files_sha256"]["sm8475-motorola-oneli.dtb"],
                "modules_dep":b["modules_dep_sha256"]},
      "modules_sha256":mods,
      "qemu_runtime_module":v["qemu_runtime_module"],
      "qemu_virt_config":{"machine":"virt","console":"ttyAMA0",
                          "virtio_transport":"mmio","root_disk":"virtio-blk",
                          "network":"virtio-net","root_fs":"ext4",
                          "required_builtin":BUILTINS,
                          "required_enabled":["CONFIG_MODULES"],
                          "required_loadable":["CONFIG_DUMMY"]},
      "toolchain":{"compiler":"Boot logs/toolchain.txt","linker":"Boot logs/toolchain.txt",
                   "build_command":"Drzet/linux razr-oneli-combined.yml"},
      "commits":[{"original":x["original"],"applied":x["result"]}
                 for x in b["replayed_commits"]],
      "evidence":{"modpost_completed":True,"oneli_dtb_compiled":True,
                  "phone_tested":False},
      "producer":{"interface":"oneli-combined-artifact-interface-v1",
                  "original_build_manifest_sha256":sha(root/"build-manifest.json"),
                  "original_preflight_sha256":sha(root/"qemu-native-inputs.v3.preflight.json"),
                  "source_config_project_commit":b["source_config_project_commit"]}}
    m=out/"manifests"
    m.mkdir()
    (m/"combined-kernel-build-v1.json").write_text(json.dumps(manifest,indent=2)+"\n")
    audit=out/"producer-record"
    audit.mkdir()
    for name in ("build-manifest.json","module-sha256.json",
                 "firmware-qemu-virt.json","qemu-native-inputs.v3.preflight.json","SHA256SUMS"):
        shutil.copy2(root/name,audit/name)
    shutil.copy2(root/"logs/toolchain.txt",audit/"toolchain.txt")
    print("BOOT_COMBINED_BUNDLE_NORMALIZED release="+release+
          " modules="+str(len(mods)))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--boot-root",type=Path,required=True)
    p.add_argument("--output-root",type=Path,required=True)
    a=p.parse_args()
    try: convert(a.boot_root,a.output_root)
    except (OSError,ValueError,KeyError,TypeError) as e:
        p.exit(1,"BOOT_BUNDLE_ADAPTER_FAILED: "+str(e)+"\n")
if __name__=="__main__":
    main()
