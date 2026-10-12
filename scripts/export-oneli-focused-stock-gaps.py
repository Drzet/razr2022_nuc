#!/usr/bin/env python3
"""Follow-up ONLY for gaps in accepted Motorola six-FDT filtered export.

Only previously SHA256-pinned dtbo/vendor_boot/boot ZIP members are retrieved
using existing ZIP64 HTTP Range parser, not the entire ROM, super or radio.
Export narrowly selected ORIGINAL FDT properties, with no raw DTB payloads.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import struct
from pathlib import Path

EXPECTED = {
    "dtbo.img":"daf02eb24af55cf4c20569db51b5bca70f0550d035846672ef3054f0c0484bd0",
    "vendor_boot.img":"1c27e22565f6f50919812bfcb5254cea2f3b629d98f5c26a7b54f5ece452036e",
    "boot.img":"287b3b5e3c61dec6a40f2b9203942b57533df206b0ed2ef16ecdb6bbe01e305d",
}
BASE_FILTER = re.compile(
    r"/soc/qcom,kgsl-3d0@3d00000(?:/qcom,gpu-pwrlevels(?:/.*)?)?$|"
    r"/soc/qcom,gmu@3d69000(?:/.*)?$|"
    r"/soc/qcom,vidc@aa00000(?:/.*)?$|"
    r"(?i:gpu-pwrlevel|gpu-pwrlevels|gmu|voter|bus-vote|gpu-bus|"
    r"rpmh-regulator|rpmhpd|cx\.lvl|mxc\.lvl|gfx\.lvl|"
    r"qcom,gdsc@3d99|qcom,gdsc@aaf|interconnect@|mmss-noc|gem-noc|"
    r"mc-virt|config-noc|videocc|video-cc|clock-controller@aaf)")
OVERLAY_FILTER = re.compile(r"^/fragment@48(?:/.*)?$")
LIMIT_NODES = 700
LIMIT_BYTES = 10000


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def module(path, label):
    spec=importlib.util.spec_from_file_location(label, path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def fields(fdt, at, identity, parse):
    nodes, fmt = parse.parse_fdt(fdt, at)
    chosen = []
    filter_re = BASE_FILTER if identity["member"] == "vendor_boot.img" else OVERLAY_FILTER
    for node in nodes:
        if not filter_re.search(node["path"]):
            continue
        props = {}
        for key, value in sorted(node["properties"].items()):
            if parse.SENSITIVE.search(key):
                props[key] = {"state":"redacted_identifier", "length":len(value),
                              "sha256":sha(value)}
                continue
            if len(value) > LIMIT_BYTES:
                props[key] = {"state":"oversized_raw_not_published", "length":len(value),
                              "sha256":sha(value)}
                continue
            props[key] = parse.render_prop(key,value)
        chosen.append({"path":node["path"],"properties":props})
        if len(chosen)>LIMIT_NODES:
            raise ValueError("too many focused nodes")
    return {"fdt_sha256":fmt["sha256"], "size":fmt["total_size"],
            "fdt_node_count":len(nodes), "focal_node_count":len(chosen),
            "source":identity, "filter":filter_re.pattern,
            "nodes":chosen, "node_absence_is_checked":True}


def boot_v4_header(blob):
    if blob[:8] != b"ANDROID!":
        raise ValueError("boot image magic absent")
    kernel_len, rd_len, os_version, header_size = struct.unpack_from("<4I",blob,8)
    header_version = struct.unpack_from("<I",blob,40)[0]
    if header_version != 4 or header_size < 1584:
        raise ValueError("expected Android boot v4")
    # V3/v4 boot header occupies first 4096 bytes; kernel and ramdisk are
    # page-aligned with page fixed 4096 in the format, not phone-flash offsets.
    at=4096
    kernel=blob[at:at+kernel_len]
    at += ((kernel_len+4095)//4096)*4096
    ramdisk=blob[at:at+rd_len]
    at += ((rd_len+4095)//4096)*4096
    sig_bytes=struct.unpack_from("<I",blob,1580)[0]
    signature=blob[at:at+sig_bytes]
    if len(kernel)!=kernel_len or len(ramdisk)!=rd_len or len(signature)!=sig_bytes:
        raise ValueError("truncated boot v4 sections")
    reserved=list(struct.unpack_from("<4I",blob,24))
    cmdline=blob[44:1580].split(b"\0",1)[0].decode("ascii","replace")
    return {"format":"Android boot v4",
            "os_version_packed":os_version,"header_size":header_size,
            "header_version":header_version,"reserved_u32":reserved,
            "kernel_bytes":kernel_len,"kernel_sha256":sha(kernel),
            "ramdisk_bytes":rd_len,"ramdisk_sha256":sha(ramdisk),
            "signature_bytes":sig_bytes,"signature_sha256":sha(signature),
            "cmdline_sha256":sha(cmdline.encode()), "cmdline_length":len(cmdline),
            "head_16_hex":blob[:16].hex(),
            "image_member_sha256":sha(blob),
            "not_a_bootloader_acceptance_or_packaging_recipe":True}


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",required=True,type=Path)
    args=a.parse_args()
    base=Path(__file__).parent
    zipmod=module(base/"inspect-oneli-stock-ranges.py","ziprange")
    dt=module(base/"export-oneli-stock-fdts.py","dtparse")
    zipmod.TARGETS=tuple(EXPECTED)
    zipmod.COMPRESSED_CAP=110*1024*1024
    zipmod.EXPANDED_CAP=125*1024*1024
    directory,_=zipmod.metadata(zipmod.STOCK_URL)
    result={"scope":"focused_source_properties_only_not_runtime_composition",
            "stock_zip_sha256_pinned":"620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c",
            "member_sha256":{},"per_fdt_focus":[]}
    for name in EXPECTED:
        if name not in directory:
            raise ValueError(f"ZIP member {name} not present")
        blob=zipmod.member(zipmod.STOCK_URL,name,directory[name])
        if sha(blob)!=EXPECTED[name]:
            raise ValueError(f"member mismatch {name}")
        result["member_sha256"][name] = sha(blob)
        if name=="dtbo.img":
            if struct.unpack_from(">I",blob)[0]!=0xd7b7ab1e:
                raise ValueError("invalid dtbo table magic")
            total, header_sz, entry_sz, count, entry_off = struct.unpack_from(">5I",blob,4)
            if count!=4 or entry_off+count*entry_sz>total:
                raise ValueError("wrong bounded DTBO count")
            for i in range(count):
                sz,pos,*_ = struct.unpack_from(">8I",blob,entry_off+i*entry_sz)
                if pos+sz>total:
                    raise ValueError("DTBO bounds")
                result["per_fdt_focus"].append(fields(blob[pos:pos+sz],0,
                    {"member":name,"entry":i,"offset":pos},dt))
        elif name=="vendor_boot.img":
            if blob[:8]!=b"VNDRBOOT":
                raise ValueError("no vendor_boot")
            page=struct.unpack_from("<I",blob,12)[0]
            hdr=struct.unpack_from("<I",blob,2096)[0]
            ram=struct.unpack_from("<I",blob,24)[0]
            dtb_sz=struct.unpack_from("<I",blob,2100)[0]
            off=((hdr+page-1)//page + (ram+page-1)//page)*page
            region=blob[off:off+dtb_sz]
            fdts,invalid=dt.region_fdts(region)
            if len(fdts)!=2:
                raise ValueError(f"expected two FDTs, got {len(fdts)}, invalid {invalid[:4]}")
            for f in fdts:
                pos=f["byte_offset_in_member_or_region"]
                result["per_fdt_focus"].append(fields(region,pos,
                    {"member":name,"offset_in_region":pos,
                     "root_msm_id":f["root_ids"].get("qcom,msm-id",{}).get("cells_be_u32")},dt))
            result["vendor_boot_header"]={
                "version":struct.unpack_from("<I",blob,8)[0],"page_size":page,
                "header_size":hdr,
                "kernel_addr":struct.unpack_from("<I",blob,16)[0],
                "ramdisk_addr":struct.unpack_from("<I",blob,20)[0],
                "tags_addr":struct.unpack_from("<I",blob,2076)[0],
                "dtb_addr":struct.unpack_from("<Q",blob,2104)[0],
                "base_FDT_count":len(fdts),"region_offset":off,
                "region_size":dtb_sz,"region_sha256":sha(region)}
        elif name=="boot.img":
            result["boot_v4_header"]=boot_v4_header(blob)
        print(name,"sha256",sha(blob),flush=True)
    assert len(result["per_fdt_focus"])==6
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("focused_json_size",args.out.stat().st_size,flush=True)

if __name__=="__main__":
    main()
