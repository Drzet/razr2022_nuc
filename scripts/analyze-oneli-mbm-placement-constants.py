#!/usr/bin/env python3
"""Bounded static literals for oneli ABL kernel address routine (read-only)."""
import hashlib,importlib.util,json,struct,subprocess,tempfile,re
from pathlib import Path
source=Path(__file__).with_name("inspect-oneli-mbm-public-reference.py")
spec=importlib.util.spec_from_file_location("oneli_stock",source)
src=importlib.util.module_from_spec(spec);spec.loader.exec_module(src)
OFFSETS={
"64bit_kernel_fallback_load":0xc4920,
"64bit_reserved_end_fallback":0xc4924,
"32bit_kernel_fallback_load":0xc492c,
"32bit_reserved_end_fallback":0xc4928,
"kernel_var_name":0xdf020,
"kernel_size_var_name":0xdf00a,
"FDT_query_name_1":0xde96f,
"FDT_query_name_2":0xde977,
"FDT_override_debug":0xde98d,
"base_memory_log":0xde9f8,
}
def pe_sections(data):
    """Validate PE headers and retain virtual and raw section boundaries."""
    if len(data)<0x40 or data[:2]!=b"MZ":
        raise ValueError("not a PE DOS header")
    peoff=struct.unpack_from("<I",data,0x3c)[0]
    if peoff+24>len(data) or data[peoff:peoff+4]!=b"PE\0\0":
        raise ValueError("not a PE signature")
    machine,nsecs=struct.unpack_from("<HH",data,peoff+4)
    if machine!=0xaa64 or not (1<=nsecs<=96):
        raise ValueError("unexpected PE machine or section count")
    optbytes=struct.unpack_from("<H",data,peoff+20)[0]
    start=peoff+24+optbytes
    if start+nsecs*40>len(data):
        raise ValueError("truncated PE section table")
    sections=[]
    for i in range(nsecs):
        pos=start+40*i
        name=data[pos:pos+8].split(b"\0",1)[0].decode("ascii","replace")
        virtual_size,rva,raw_size,raw_offset=struct.unpack_from("<IIII",data,pos+8)
        if raw_offset+raw_size>len(data):
            raise ValueError("PE section raw bytes truncated: "+name)
        sections.append({"name":name,"rva":rva,"virtual_size":virtual_size,
                         "raw_size":raw_size,"file_offset":raw_offset})
    return sections

def rva_to_raw(data,sections,rva,length=1):
    """Read only raw-backed RVA spans, never treat an RVA as a file offset."""
    if rva<0 or length<0:
        raise ValueError("negative RVA or span")
    for s in sections:
        if s["rva"]<=rva and rva+length<=s["rva"]+s["raw_size"]:
            off=s["file_offset"]+(rva-s["rva"])
            if off+length>len(data):
                raise ValueError("PE RVA maps beyond end of file")
            return off
    raise ValueError(f"unmapped or virtual-only PE RVA {rva:#x} length {length}")

def read_rva(data,sections,rva,length):
    off=rva_to_raw(data,sections,rva,length)
    return data[off:off+length]

def cstr(data,off,maxbytes=120,utf16=False):
    b=data[off:off+maxbytes]
    if utf16:
        # Termination is tested at aligned UTF-16LE code-unit boundaries only.
        # An unaligned byte-pair search otherwise discards the final letter.
        for pos in range(0,len(b)-1,2):
            if b[pos:pos+2]==b"\0\0":
                return b[:pos].decode("utf-16le",errors="strict")
        raise ValueError("unterminated UTF-16LE literal")
    return b.split(b"\0",1)[0].decode("ascii","replace")

def literal(data,sections,rva,maxbytes=120,utf16=False):
    off=rva_to_raw(data,sections,rva,1)
    s=next(s for s in sections if s["rva"]<=rva<s["rva"]+s["raw_size"])
    raw_available=s["raw_size"]-(rva-s["rva"])
    return cstr(data,off,min(maxbytes,raw_available),utf16=utf16)

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
    sections=pe_sections(p)
    literal_rvas={name:addr for name,addr in OFFSETS.items()}
    for name,addr in literal_rvas.items():
        rva_to_raw(p,sections,addr,4 if "fallback" in name else 1)
    rva_to_raw(p,sections,0xeeb20,16)
    report={
        "pe_sections":sections,
        "checked_literal_rvas":{k:{"rva":hex(v),"raw_offset":hex(rva_to_raw(p,sections,v)),
                                    "section":next(s["name"] for s in sections if s["rva"]<=v<s["rva"]+s["raw_size"])}
                                for k,v in literal_rvas.items()},
        "rva_mapping_checked_for_constants_and_strings":True,
        "abl_loader_sha256":hashlib.sha256(p).hexdigest(),
        "stock_member_sha256":meta["sha256"],"codebase":"PE RVAs; no physical address implied",
        "constant_little_endian_u32":{
            name:{"rva":hex(addr),"u32_dec":struct.unpack("<I",read_rva(p,sections,addr,4))[0],
                  "u32_hex":hex(struct.unpack("<I",read_rva(p,sections,addr,4))[0])}
             for name,addr in OFFSETS.items() if "fallback" in name
        },
        "selected_literals":{
            name:{"rva":hex(addr),"ascii_or_utf16":literal(p,sections,addr,utf16=name in ("kernel_var_name","kernel_size_var_name"))}
            for name,addr in OFFSETS.items() if "fallback" not in name
        },
        "nearby_literals":[{
            "rva":hex(a),"ascii":literal(p,sections,a)} for a in range(0xde940,0xde9e0,1)
            if read_rva(p,sections,a,1)!=b"\0" and (a==0xde940 or read_rva(p,sections,a-1,1)==b"\0") and
            len(literal(p,sections,a))>=4
        ],
        "kernel_var_uefi_guid_bytes":read_rva(p,sections,0xeeb20,16).hex(),
        "verified_zip_member_crc":True,
        "no_firmware_bytes_retained":True,
        "on_device_values_not_observed":True
    }
    loc=Path("evidence");loc.mkdir(exist_ok=True)
    (loc/"oneli-mbm-placement-constants.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
