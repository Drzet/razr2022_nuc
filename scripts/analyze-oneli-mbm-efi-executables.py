#!/usr/bin/env python3
"""Reconstruct oneli ABL/UEFI firmware volumes in ephemeral CI, export evidence not bytes."""
import base64, hashlib, importlib.util, json, os, re, shutil, struct, subprocess, tempfile
from pathlib import Path

p=Path(__file__).with_name("inspect-oneli-mbm-public-reference.py")
s=importlib.util.spec_from_file_location("stock_member",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

KEYS=("fastboot","boot","kernel","ramdisk","dtbo","bootconfig","avb","verified",
      "memory","memmap","cmdline","vendor","loadimage","getboot","getdtb",
      "unlock","bootimg","bootimage","console","uart","relocat","fdt",
      "getvar","download","usb")
def strings(data,utf16=False):
    patt=rb"(?:[\x20-\x7e]\x00){7,190}" if utf16 else rb"[\x20-\x7e]{7,190}"
    for mm in re.finditer(patt,data):
        try:v=mm.group(0).decode("utf-16le" if utf16 else "ascii")
        except UnicodeError:continue
        if any(x in v.lower() for x in KEYS):
            yield dict(offset=mm.start(),encoding="u16" if utf16 else "ascii",text=v[:190])

def fv_parses(b):
    v=[]
    for mm in re.finditer(b"_FVH",b):
        i=mm.start()-40
        if i<0 or i+56>len(b):continue
        sz=struct.unpack_from("<Q",b,i+32)[0]
        if 72<=sz<=len(b)-i and sz<10*1024*1024:
            v.append((i,b[i:i+sz]))
    return v

def command(c,timeout=100):
    try:
        r=subprocess.run(c,capture_output=True,text=True,errors="replace",timeout=timeout)
        return dict(returncode=r.returncode,stdout=r.stdout[:8000],stderr=r.stderr[:2000])
    except Exception as e:return dict(error=str(e))

def parse_efi_file(b):
    if b[:2]!=b"MZ" or len(b)<128:return {}
    off=struct.unpack_from("<I",b,0x3c)[0]
    if off>4096 or off+256>len(b) or b[off:off+4]!=b"PE\0\0":return {}
    machine,nsects=struct.unpack_from("<HH",b,off+4)
    optsz=struct.unpack_from("<H",b,off+20)[0]
    opt=off+24;magic=struct.unpack_from("<H",b,opt)[0]
    image_base=struct.unpack_from("<Q" if magic==0x20b else "<I",b,opt+24 if magic==0x20b else opt+28)[0]
    entry_rva=struct.unpack_from("<I",b,opt+16)[0]
    return dict(machine=hex(machine),sections=nsects,magic=hex(magic),
                entry_rva=hex(entry_rva),image_base=hex(image_base))

def main():
    image,meta=m.member_download()
    pieces,_=m.submembers(image)
    out=[];summary=[]
    with tempfile.TemporaryDirectory(prefix="oneli-mbm-research-") as td:
        tmp=Path(td)
        for name,_,data in pieces:
            if name not in ("abl.elf","uefi.elf"):continue
            for fv_index,(offset,fv) in enumerate(fv_parses(data)):
                input_path=tmp/f"{name}-{fv_index}.fv"
                dest=tmp/f"{name}-{fv_index}-extracted"
                input_path.write_bytes(fv)
                dest.mkdir()
                cmd=command(["uefi-firmware-parser","-b","-e","-o",str(dest),str(input_path)],150)
                records=[]
                files=sorted((p for p in dest.rglob("*") if p.is_file()),key=lambda p:str(p))
                for path in files:
                    body=path.read_bytes()
                    if len(body)>15*1024*1024:continue
                    pe=parse_efi_file(body)
                    matches=list(strings(body))
                    matches+=list(strings(body,True))
                    if len(records)>=400:break
                    row=dict(relative_path=str(path.relative_to(dest)),
                             size=len(body),sha256=hashlib.sha256(body).hexdigest(),
                             pe=pe,
                             relevant_strings_count=len(matches),
                             relevant_strings=matches[:110])
                    # Preserve bounded disassembly of the beginning of each PE,
                    # enough to prove architecture/entry point without raw bytes.
                    if pe and pe["machine"] in ("0xaa64","0x1c4"):
                        arg=["llvm-objdump","-d","--no-show-raw-insn",str(path)]
                        q=command(arg,75)
                        row["objdump_first"]=(q.get("stdout") or "")[:5000]
                        row["objdump_error"]=q.get("stderr","")[:900]
                    records.append(row)
                out.append(dict(outer_name=name,fv_offset=offset,volume_sha256=hashlib.sha256(fv).hexdigest(),
                                volume_size=len(fv),parser_stdout=cmd.get("stdout","")[:4500],
                                parser_stderr=cmd.get("stderr","")[:2500],parser_code=cmd.get("returncode"),
                                extracted_files=len(files),records=records))
                summary.append(f"{name} FV[{fv_index}] {len(fv)} bytes {len(files)} extracted files; "
                               f"{sum(bool(r['pe']) for r in records)} PE images")
                summary.extend(f"  {r['relative_path']} {r['size']} bytes {r['pe'].get('machine','?')} "
                               f"{r['relevant_strings_count']} keyword strings"
                               for r in records if r["pe"] or r["relevant_strings_count"]>3)
    report=dict(bootloader_member_sha256=meta["sha256"],
                strict_zip_crc_verified=True, full_zip_not_downloaded=True,
                only_public_reference_image=True,no_runtime_claim=True,
                no_proprietary_firmware_retained=True,
                parser_version="uefi-firmware 1.16",volumes=out)
    p=Path("evidence");p.mkdir(exist_ok=True)
    (p/"oneli-mbm-efi-executable-inventory.json").write_text(json.dumps(report,indent=2))
    (p/"oneli-mbm-efi-executable-inventory.txt").write_text("\n".join(summary)+"\n")
    print("\n".join(summary[:150]))
if __name__=="__main__":main()
