#!/usr/bin/env python3
"""Bounded static literals for oneli ABL kernel address routine (read-only)."""
import hashlib,importlib.util,json,struct,subprocess,tempfile,re
from pathlib import Path
source=Path(__file__).with_name("inspect-oneli-mbm-public-reference.py")
spec=importlib.util.spec_from_file_location("oneli_stock",source)
src=importlib.util.module_from_spec(spec);spec.loader.exec_module(src)
OFFSETS={
"64bit_kernel_fallback_load":0xc40920,
"64bit_reserved_end_fallback":0xc40924,
"32bit_kernel_fallback_load":0xc40928,
"32bit_reserved_end_fallback":0xc4092c,
"kernel_var_name":0xdf020,
"kernel_size_var_name":0xdf00a,
"FDT_query_name_1":0xde96f,
"FDT_query_name_2":0xde977,
"FDT_override_debug":0xde98d,
"base_memory_log":0xde9f8,
}
def cstr(data,off,maxbytes=120):
    b=data[off:off+maxbytes]
    if off==0xdf020 or off==0xdf00a:
        try: return b[:b.index(b"\0\0")//2*2].decode("utf-16le")
        except Exception:pass
    return b.split(b"\0",1)[0].decode("ascii","replace")
def main():
    blob,meta=src.member_download()
    parts,_=src.submembers(blob)
    abl=next(v for n,_,v in parts if n=="abl.elf")
    with tempfile.TemporaryDirectory(prefix="mbm-constants-") as td:
        root=Path(td);i=abl.find(b"_FVH")-40;n=struct.unpack_from("<Q",abl,i+32)[0]
        inp=root/"abl.fv";inp.write_bytes(abl[i:i+n]);out=root/"ex";out.mkdir()
        q=subprocess.run(["uefi-firmware-parser","-b","-e","-o",str(out),str(inp)],
            capture_output=True,text=True,timeout=150)
        if q.returncode:raise RuntimeError(q.stderr[:1000])
        candidates=[x for x in out.rglob("section1.pe")
                    if "file-9ab20751-6179-47f8-af85-796468678f92" in str(x)]
        if len(candidates)!=1:raise ValueError("Loader PE not unique")
        p=candidates[0].read_bytes()
    report={
        "abl_loader_sha256":hashlib.sha256(p).hexdigest(),
        "stock_member_sha256":meta["sha256"],"codebase":"PE RVAs; no physical address implied",
        "constant_little_endian_u32":{
            name:{"rva":hex(addr),"u32_dec":struct.unpack_from("<I",p,addr)[0],
                  "u32_hex":hex(struct.unpack_from("<I",p,addr)[0])}
             for name,addr in OFFSETS.items() if "fallback" in name
        },
        "selected_literals":{
            name:{"rva":hex(addr),"ascii_or_utf16":cstr(p,addr)}
            for name,addr in OFFSETS.items() if "fallback" not in name
        },
        "nearby_literals":[{
            "rva":hex(a),"ascii":cstr(p,a)} for a in range(0xde940,0xde9e0,1)
            if p[a:a+1]!=b"\0" and (a==0xde940 or p[a-1]==0) and
            len(cstr(p,a))>=4
        ],
        "kernel_var_uefi_guid_bytes":p[0xeeb20:0xeeb30].hex(),
        "verified_zip_member_crc":True,
        "no_firmware_bytes_retained":True,
        "on_device_values_not_observed":True
    }
    loc=Path("evidence");loc.mkdir(exist_ok=True)
    (loc/"oneli-mbm-placement-constants.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
