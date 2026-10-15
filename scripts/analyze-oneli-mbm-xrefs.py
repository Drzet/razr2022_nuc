#!/usr/bin/env python3
"""Bounded AArch64 xref disassembly for oneli bootloader's decompressed PE modules."""
import bisect, hashlib, importlib.util, json, re, struct, subprocess, tempfile
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
import pefile

modpath=Path(__file__).with_name("inspect-oneli-mbm-public-reference.py")
spec=importlib.util.spec_from_file_location("oneli_member",modpath)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

PATTERNS=[
    ("fastboot_boot_lock",r"Fastboot boot command is not available in locked device"),
    ("fastboot_boot_header",r"Invalid Boot image Header"),
    ("fastboot_boot_load",r"Failed to load/authenticate boot image"),
    ("fastboot_download",r"Download Finished|Fastboot Buffer Size allocated|Fastboot: Processing commands"),
    ("ram_boot",r"LoadImageAndAuth|BootLinux\(\)|Failed to boot Linux"),
    ("boot_kernel",r"Kernel not preloaded|PropagateKernelSocInfo|kernel_addr|kernel_base|KernelBaseAddr"),
    ("dt_overlay",r"DTBO|DTB|UFDT|DeviceTree|Fdt|overlay"),
    ("ramdisk",r"ramdisk|vendor_boot|bootconfig|cmdline"),
    ("verification",r"Device is unlocked! Skipping verification!|VerifyImage|GetBootState|SendBootState"),
    ("device_lock",r"device.*lock|unlock|locked device"),
    ("boot_config",r"boot.*config|BOOT LUN|boot_mode"),
    ("memmap",r"memory map|MemMap|memmap|AllocatePages"),
]
CHECK=re.compile("|".join("(?:"+q+")" for _,q in PATTERNS),re.I)
MD=Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
MD.detail=False

def find_strings(data):
    strings=[]
    for typ,pat,enc in (("ascii",rb"[\x20-\x7e]{9,240}","ascii"),
                          ("utf16le",rb"(?:[\x20-\x7e]\x00){9,240}","utf-16le")):
        for mt in re.finditer(pat,data):
            s=mt.group().decode(enc)
            if CHECK.search(s):
                strings.append((mt.start(),s,typ))
    return strings

def to_rva(pe,off):
    if off < pe.OPTIONAL_HEADER.SizeOfHeaders:return off
    for sec in pe.sections:
        start=sec.PointerToRawData
        if start<=off<start+sec.SizeOfRawData:
            return sec.VirtualAddress+off-start
    return None

def find_ref(table, target):
    # Match start or interior of literal (many compiler optimizations reference substrings).
    ix=bisect.bisect_right(table,(target,'\uffff'))-1
    for j in (ix,ix+1):
        if 0<=j<len(table):
            addr,s,k,off=table[j]
            if addr<=target<addr+(len(s)*2 if k=="utf16le" else len(s)):
                return (addr,s,k,off)
    return None

def xrefs(pe, table):
    sec_results={}
    addrs=[t[0] for t in table]
    if not table:return sec_results
    for sec in pe.sections:
        if not sec.Characteristics & 0x20000000:continue
        ins=sec.get_data()
        if len(ins)<8:continue
        base=sec.VirtualAddress
        refs=[]
        for i in range(0,len(ins)-4,4):
            word=struct.unpack_from("<I",ins,i)[0]
            if word & 0x9f000000 != 0x90000000:continue
            immhi=(word>>5)&0x7ffff
            immlo=(word>>29)&3
            imm21=(immhi<<2)|immlo
            if imm21 & (1<<20):imm21-=1<<21
            pc=base+i
            page=(pc &~4095)+(imm21<<12)
            reg=word &31
            for j in range(4,37,4):
                if i+j+4>len(ins):break
                nxt=struct.unpack_from("<I",ins,i+j)[0]
                rd=nxt &31
                rn=(nxt>>5)&31
                off=None
                kind=None
                if (nxt & 0xff000000)==0x91000000 and rn==reg:
                    off=((nxt>>10)&0xfff)<<(12 if ((nxt>>22)&1) else 0)
                    kind="adrp-add"
                elif (nxt&0xffc00000)==0xf9400000 and rn==reg:
                    off=((nxt>>10)&0xfff)*8
                    kind="adrp-ldr-ptr"
                if off is None:continue
                target=page+off
                match=find_ref(table,target)
                if match is None:continue
                a,txt,typ,fileoff=match
                snippet_start=max(0,i-28)
                snippet_end=min(len(ins),i+j+68)
                snippet="\n".join(f"{v.address:08x}  {v.mnemonic} {v.op_str}"
                     for v in MD.disasm(ins[snippet_start:snippet_end],base+snippet_start))
                refs.append(dict(string_rva=hex(a),string_file_offset=hex(fileoff),
                                 string=txt[:200],encoding=typ,ref_pc=hex(pc),
                                 ref_kind=kind,target_rva=hex(target),
                                 code_excerpt=snippet[:2200]))
                if len(refs)>2000:break
        sec_results[sec.Name.decode("ascii","replace").strip("\0")]=refs
    return sec_results

def main():
    blob,meta=mod.member_download()
    comps,_=mod.submembers(blob)
    reports=[]
    with tempfile.TemporaryDirectory(prefix="oneli-code-") as td:
        root=Path(td)
        for name,_,data in comps:
            if name not in ("abl.elf","uefi.elf"):continue
            idx=data.find(b"_FVH")-40
            size=struct.unpack_from("<Q",data,idx+32)[0]
            fp=root/(name+".fv");fp.write_bytes(data[idx:idx+size])
            target=root/(name+"-files");target.mkdir()
            p=subprocess.run(["uefi-firmware-parser","-b","-e","-o",str(target),str(fp)],
                             capture_output=True,text=True,timeout=140)
            if p.returncode!=0:raise RuntimeError("UEFI parser error "+p.stderr[:700])
            modules=[]
            for path in sorted(target.rglob("*.pe")):
                contents=path.read_bytes()
                if contents[:2]!=b"MZ" or len(contents)>3000000:continue
                try:pe=pefile.PE(data=contents,fast_load=True)
                except Exception:continue
                if pe.FILE_HEADER.Machine!=0xaa64:continue
                strings=find_strings(contents)
                fulltext=" ".join(s for _,s,_ in strings).lower()
                must=(name=="abl.elf" or
                      any(term in fulltext for term in
                          ("verifiedbootdxe","vendor_boot","bootlinux",
                           "kernel not preloaded","fastboot boot","boot boot",
                           "ramdisk_addr","kernelbaseaddr","bootconfig",
                           "loadimageandauth")))
                if not must:continue
                table=sorted((to_rva(pe,at),s,typ,at) for at,s,typ in strings if to_rva(pe,at)!=None)
                refs=xrefs(pe,table)
                refs_flat=[r for rows in refs.values() for r in rows]
                report=dict(outer=name,
                            module_guid=next((part[5:] for part in path.parts if part.startswith("file-")),""),
                            path=str(path.relative_to(target)),
                            image_size=len(contents),
                            image_sha256=hashlib.sha256(contents).hexdigest(),
                            entrypoint=hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
                            sections=[dict(name=s.Name.decode("ascii","replace").strip("\0"),
                                           rva=hex(s.VirtualAddress),
                                           raw_offset=hex(s.PointerToRawData),size=s.SizeOfRawData,
                                           flags=hex(s.Characteristics)) for s in pe.sections],
                            strings=[dict(file_offset=hex(off),rva=hex(to_rva(pe,off)),text=s[:190],encoding=typ)
                                     for off,s,typ in strings][:600],
                            xrefs=refs_flat[:550],
                            xrefs_found=len(refs_flat))
                modules.append(report)
            reports+=modules
    result=dict(stock_bootloader_sha256=meta["sha256"],verified_zip_crc=True,
                no_binary_uploaded=True,static_xrefs_not_runtime_behavior=True,
                module_reports=reports)
    ev=Path("evidence");ev.mkdir(exist_ok=True)
    (ev/"oneli-mbm-aarch64-disassembly-xrefs.json").write_text(json.dumps(result,indent=2))
    summary=[f"bootloader.img sha256 {meta['sha256']}",f"analysed selected modules {len(reports)}"]
    for r in reports:
        summary.append(f"{r['outer']} {r['module_guid']} size {r['image_size']} "
                       f"candidate strings {len(r['strings'])} direct xrefs {r['xrefs_found']}")
        for v in r["xrefs"]:
            if any(k in v["string"].lower() for k in
                   ("fastboot boot command","invalid boot image header",
                    "failed to load/authenticate boot image","device is unlocked",
                    "bootlinux() failed","loadimageandauth failed",
                    "kernel not preloaded","vendor_boot","bootconfig")):
                summary.append(f"  STRING {v['string']!r} xref {v['ref_pc']}\n{v['code_excerpt']}\n")
    (ev/"oneli-mbm-aarch64-disassembly-xrefs.txt").write_text("\n".join(summary)+"\n")
    print("\n".join(summary)[:19000])
if __name__=="__main__":main()
