#!/usr/bin/env python3
"""Research-only static disassembly of oneli ABL Linux loader address path.

FIRMWARE BYTES NEVER WRITTEN TO ARTIFACTS; only short instruction listings and
referenced offsets. All file members acquired with bounded verified byte ranges.
"""
import hashlib, importlib.util, json, re, struct, subprocess, tempfile
from collections import Counter
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN, CS_OPT_DETAIL

source=Path(__file__).with_name("inspect-oneli-mbm-public-reference.py")
spec=importlib.util.spec_from_file_location("oneli_stock",source)
src=importlib.util.module_from_spec(spec);spec.loader.exec_module(src)
C=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN);C.detail=False

WINDOWS={
"BOOTLINUX_ENTRY":(0x2b40,0x3030),
"FASTBOOT_BOOT":(0x89c0,0x9370),
"PREP_IMAGE_MEMMAP":(0x60300,0x62240),
"KERNEL_RAMDISK_AND_SIZE":(0x62240,0x66cb0),
"DTB_BASE_OFFSET_AND_RELOCATION":(0x66cb0,0x69ae0),
"KERNEL_BASE_VAR_GET":(0x6b1c0,0x6bab0),
"LOAD_ADDR_AND_DTB":(0x69ae0,0x6b1c0),
"POST_VAR_LOAD":(0x6bab0,0x6fc00),
"FINAL_BOOTLINUX_PASS":(0x86200,0x89500),
}
RELATED_CONSTANTS=[0xa0000000,0x80000000,0x8000,0x1000000,0x1f00000,0x200000,
                   0x3200000,0x32c0000,0x4000000,0x1000,0x10000]
TARGETS=(0x2d94,0x65708,0x6b598,0x6778c,0x65fbc,0x65eb4,0x66014,
         0x66f00,0x6a000,0x8d00,0x8dbc,0x67d60,0x68264,0x6b680)

def main():
    blob,archive=src.member_download()
    components,_=src.submembers(blob)
    abl=next(v for n,_,v in components if n=="abl.elf")
    pe_data=None
    with tempfile.TemporaryDirectory(prefix="oneli-placement-") as temp:
        base=Path(temp)
        # ABL first EFI FV (contains LinuxLoader)
        at=abl.find(b"_FVH")-40
        if at<0:raise ValueError("missing ABL firmware FV")
        length=struct.unpack_from("<Q",abl,at+32)[0]
        vf=base/"abl.fv";vf.write_bytes(abl[at:at+length])
        ex=base/"out";ex.mkdir()
        r=subprocess.run(["uefi-firmware-parser","-b","-e","-o",str(ex),str(vf)],
                          capture_output=True,text=True,timeout=130)
        if r.returncode:raise RuntimeError(r.stderr[-1000:])
        files=list(ex.rglob("section1.pe"))
        choices=[p for p in files if "file-9ab20751-6179-47f8-af85-796468678f92" in str(p)]
        if len(choices)!=1:raise ValueError(f"Expected known ABL LinuxLoader {len(choices)}")
        pe_data=choices[0].read_bytes()
    if pe_data[:2]!=b"MZ":raise ValueError("not valid PE/MZ")
    pe_off=struct.unpack_from("<I",pe_data,0x3c)[0]
    if pe_data[pe_off:pe_off+4]!=b"PE\0\0" or struct.unpack_from("<H",pe_data,pe_off+4)[0]!=0xaa64:
        raise ValueError("unexpected ARM64 PE architecture")
    # Known ABL .text was identity mapped RVA to offset; prove from section header
    off=pe_off+24+struct.unpack_from("<H",pe_data,pe_off+20)[0]
    sec=[]
    for i in range(struct.unpack_from("<H",pe_data,pe_off+6)[0]):
        pos=off+i*40
        name=pe_data[pos:pos+8].split(b"\0",1)[0].decode("ascii","replace")
        vs,rva,size,fo=struct.unpack_from("<IIII",pe_data,pos+8)
        sec.append(dict(name=name,rva=rva,raw_size=size,file_offset=fo))
    text=next(s for s in sec if s["name"]==".text")
    if text["rva"]!=text["file_offset"]:raise ValueError("RVA/raw offset differ")
    machine=pe_data[text["file_offset"]:text["file_offset"]+text["raw_size"]]
    instr=list(C.disasm(machine,text["rva"]))
    imap={i.address:i for i in instr}
    def trace(a,b):
        return [f"{ins.address:08x}  {ins.mnemonic:<9} {ins.op_str}"
                for ins in instr if a<=ins.address<b]
    out=Path("evidence");out.mkdir(exist_ok=True)
    lines=["# Oneli original Motorola ABL address path: actual AArch64 instructions",
            f"bootloader.img SHA256 {archive['sha256']}",
            f"LinuxLoader PE SHA256 {hashlib.sha256(pe_data).hexdigest()}",
            f"PE .text starts {hex(text['rva'])}; full raw text length {text['raw_size']}",
            "All addresses below are PE RVAs, NOT physical RAM addresses.",
            "Firmware code listings are partial research excerpts, not a complete executable.",
            ""]
    for k,(start,end) in WINDOWS.items():
        lines+=[f"## {k} RVA {hex(start)}..{hex(end)}",*trace(start,end),""]
    (out/"oneli-mbm-placement-relevant-disassembly.txt").write_text("\n".join(lines)+"\n")
    blmap={}
    for x in instr:
        if x.mnemonic=="bl" and x.op_str.startswith("#"):
            try:target=int(x.op_str[1:],16)
            except ValueError:continue
            blmap.setdefault(target,[]).append(x.address)
    calls=[]
    for t in TARGETS:
        calls.append(dict(target=hex(t),
                          inbound_bl=[hex(a) for a in blmap.get(t,[])][:120],
                          nearby=[(f"{x.address:08x} {x.mnemonic} {x.op_str}")
                                  for x in instr if t-72<=x.address<t+108]))
    # target references around the UEFI GetVariable and dynamic loader
    result={"stock_source_sha256":archive["sha256"],
            "abl_pe_sha256":hashlib.sha256(pe_data).hexdigest(),
            "image_sections":sec,
            "windows":{k:{"start":hex(st),"end":hex(en),
                          "instructions":len(trace(st,en))} for k,(st,en) in WINDOWS.items()},
            "selected_call_sites":calls,
            "interesting_constant_instructions":[
                {"pc":hex(x.address),"mnemonic":x.mnemonic,"operands":x.op_str}
                for x in instr
                if x.mnemonic in ("mov","movk","orr","and","add","subs","cmp")
                   and any((hex(k) in x.op_str.lower()) for k in RELATED_CONSTANTS)
            ][:2400],
            "full_zip_not_downloaded":True,
            "no_proprietary_bins_in_artifact":True,
            "verified_memory_values_not_claimed":True}
    (out/"oneli-mbm-placement-static-index.json").write_text(json.dumps(result,indent=2))
    print(f"ABL kernel load code sections disassembled: {len(instr)} instructions")
    print(f"Saved {len(WINDOWS)} windows, "+str(len(lines))+" lines")
if __name__=="__main__":main()
