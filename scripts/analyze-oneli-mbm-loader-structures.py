#!/usr/bin/env python3
"""Read-only second-pass loader structure and bounded string evidence. No firmware output."""
import hashlib, importlib.util, json, re, struct
from pathlib import Path

src=Path(__file__).with_name("inspect-oneli-mbm-public-reference.py")
spec=importlib.util.spec_from_file_location("oneli_stock_member",src)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

WORDSET=[
r"boot",r"fastboot",r"kernel",r"ramdisk",r"initrd",r"dtbo",r"dtb",r"fdt",
r"vendor",r"cmdline",r"bootconfig",r"avb",r"verified",r"partition",
r"image",r"memmap",r"memory map",r"serial",r"uart",r"uefi",
r"cache",r"relocat",r"unlocked",r"oneli",r"board.id",r"recovery",
r"system.as.root",r"snapshot",r"slot",r"motoboot",r"EDK",r"gpt",
r"bootloader",r"download",r"MMC",r"UFS",r"FvName",r"UEFI",r"error"
]
RX = re.compile("|".join(WORDSET),re.I)
def text_candidates(b):
    # printable ASCII; keep offsets so evidence can be traced to corresponding component.
    for m in re.finditer(rb"[\x20-\x7e]{7,300}",b):
        s=m.group(0).decode("ascii")
        if RX.search(s):
            yield (m.start(),"ascii",s)
    for m in re.finditer(rb"(?:[\x20-\x7e]\x00){7,300}",b):
        try: s=m.group(0).decode("utf-16le")
        except UnicodeError: continue
        if RX.search(s):
            yield (m.start(),"utf16le",s)

def efi_fvs(b):
    out=[]
    for m in re.finditer(b"_FVH",b):
        at=m.start(); start=at-40
        if start<0 or start+56>len(b):continue
        size=struct.unpack_from("<Q",b,start+32)[0]
        hl=struct.unpack_from("<H",b,start+48)[0]
        if 0<hl<=4096 and 56<=size<=len(b)-start:
            out.append(dict(offset=start, signature_offset=at, length=size,
                            header_length=hl, filesystem_guid=b[start+16:start+32].hex()))
    return out
def pe_headers(b):
    result=[]
    for m in re.finditer(b"MZ",b):
        i=m.start()
        if i+0x40>len(b):continue
        peoff=struct.unpack_from("<I",b,i+0x3c)[0]
        j=i+peoff
        if peoff>0x1000 or j+24>len(b) or b[j:j+4]!=b"PE\0\0":continue
        machine,nsects=struct.unpack_from("<HH",b,j+4)
        result.append(dict(offset=i,pe_header_offset=j,machine=hex(machine),sections=nsects))
    return result
def elf_phdr(b):
    if not b.startswith(b"\x7fELF"): return []
    cls=b[4]
    if cls==1:
        phoff=struct.unpack_from("<I",b,28)[0]
        entsize,num=struct.unpack_from("<HH",b,42)
        return [dict(type=hex(t),file_offset=off,vaddr=hex(vaddr),paddr=hex(paddr),filesz=sz,memsz=msz,
                     flags=hex(flags),align=hex(align)) for t,off,vaddr,paddr,sz,msz,flags,align in
                (struct.unpack_from("<IIIIIIII",b,phoff+entsize*i) for i in range(min(num,100)))]
    if cls==2:
        phoff=struct.unpack_from("<Q",b,32)[0]
        entsize,num=struct.unpack_from("<HH",b,54)
        return [dict(type=hex(t),file_offset=off,vaddr=hex(vaddr),paddr=hex(paddr),filesz=sz,memsz=msz,
                     flags=hex(flags),align=hex(align)) for t,flags,off,vaddr,paddr,sz,msz,align in
                (struct.unpack_from("<IIQQQQQQ",b,phoff+entsize*i) for i in range(min(num,100)))]
    return []
def check(b,name):
    strs=sorted(set(text_candidates(b)),key=lambda x:x[0])
    # Bounded evidence: all match counts, first 250 relevant strings and last 50, not full firmware strings.
    limited=strs[:250]+(strs[-50:] if len(strs)>300 else strs[250:])
    return dict(name=name,size=len(b),sha256=hashlib.sha256(b).hexdigest(),
                image_phdrs=elf_phdr(b),firmware_volumes=efi_fvs(b),
                embedded_pe_headers=pe_headers(b),
                relevant_string_total=len(strs),
                relevant_strings=[dict(offset=o,encoding=enc,text=s[:240]) for o,enc,s in limited])
def main():
    data,entry=mod.member_download()
    components,container=mod.submembers(data)
    focus={"abl.elf","uefi.elf","xbl_config.elf","xbl_s.melf"}
    selected=[check(b,name) for name,off,b in components if name in focus]
    out={"source":mod.SOURCE,"bootloader_sha256":entry["sha256"],
         "source_referenced_not_installed":True,
         "raw_components_retained":False,"runtime_behavior_verified":False,
         "analysis":selected}
    path=Path("evidence");path.mkdir(exist_ok=True)
    (path/"oneli-mbm-loader-structures.json").write_text(json.dumps(out,indent=2))
    lines=["Static firmware evidence only, not OEM loading contract.",
           f"Verified Motorola bootloader image SHA256: {entry['sha256']}"]
    for s in selected:
        lines += [f"\n{s['name']}: sha256 {s['sha256']}, {s['size']} bytes;",
                  f"  ELF load headers {len(s['image_phdrs'])} "
                  f"UEFI FVs {len(s['firmware_volumes'])} "
                  f"embedded PEs {len(s['embedded_pe_headers'])} "
                  f"selected string occurrences {s['relevant_string_total']}"]
        lines += [f"  {t['encoding']} +0x{t['offset']:x}: {t['text']}"
                  for t in s["relevant_strings"] if re.search(
                      "fastboot|kernel|ramdisk|dtbo|bootconfig|cmdline|avb|unlocked|bootloader",
                      t["text"],re.I)][:55]
    (path/"oneli-mbm-loader-structures.txt").write_text("\n".join(lines)+"\n")
    print("\n".join(lines[:28]))
if __name__=="__main__":
    main()
