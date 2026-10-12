#!/usr/bin/env python3
"""Bounded Qualcomm MDT loader structural audit from exact radio firmware headers.

One SHA-pinned radio.img ZIP member only (not full stock/super scan).
Extract exactly THREE named firmware ELF headers from NON-HLOS ext4 with debugfs.
No raw firmware payloads, image, cert or signature bytes are published.
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import struct
import subprocess
import tempfile

ZIP_HASH="620117217b2474411ce8f86c9a0e08d9b9fd82f42098c3ab65b1fcd6d976903c"
RADIO_HASH="bcaac550d908ea72f08e9a1782714a46f52d26f20ec11c7e32f97140677769ca"
NONHLOS_HASH="03d37634aa39ff9af06d3b583267e6d166996c22e7b4f06b0bcb7d7b4031a1d9"
EXT4_HASH="2ea61a0b5d31b626358f0b72c102131535f08ae3fb279b1857e646b0675416c6"
EXPECTED={
"vpu20_4v.mbn":"9582ea4c5565408bd3e5ba6f8fffc7881f226cae001b6fcd7a0c868de9add9af",
"vpu20_4v.mdt":"a276e19d4ba6f4b4b42bec7ee4497e1002582a357454d56e5e050d5f969c64b6",
"a730_zap.mdt":"f5d8a41c1380ba2b42cd742538083306d245471ac5d51139e3bc8a6168ce84d2",
}
RESERVED = {"vpu20_4v":0x700000, "a730_zap":0x2000}
PT_LOAD=1
TYPE_MASK=7<<24
TYPE_HASH=2<<24
RELOCATABLE=1<<27


def sha(b):
    return hashlib.sha256(b).hexdigest()


def mod(path, label):
    spec=importlib.util.spec_from_file_location(label,path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def extract(image, name, dest):
    # Fixed trusted filenames only, never shell evaluation or path traversal.
    if name not in EXPECTED and not (
            name.startswith(("vpu20_4v.b","a730_zap.b")) and
            len(name.split(".")[-1])==3 and name.split(".")[-1][1:].isdigit()):
        raise ValueError("unexpected firmware filename")
    command=["debugfs","-R",f"dump /image/{name} {dest}",str(image)]
    done=subprocess.run(command,text=True,capture_output=True,timeout=40)
    if done.returncode or not dest.exists():
        raise RuntimeError(f"debugfs failed extracting {name}: {done.stderr[:300]}")
    return dest.read_bytes()


def inspect_elf(data, filename):
    if data[:4]!=b"\x7fELF" or data[4]!=1 or data[5]!=1 or len(data)<52:
        raise ValueError(f"{filename}: not ELF32 little endian")
    phoff=struct.unpack_from("<I",data,28)[0]
    entsize, count=struct.unpack_from("<HH",data,42)
    if entsize!=32 or not 1<=count<=128 or phoff+count*entsize>len(data):
        raise ValueError(f"{filename}: phdr structure outside ELF")
    segments=[]
    lo=2**64-1
    hi=0
    split=False
    reloc=False
    has_hash=[]
    for i in range(count):
        typ,off,vaddr,paddr,filesz,memsz,flags,alignment=struct.unpack_from(
            "<8I",data,phoff+i*entsize)
        if filesz and (off>len(data) or filesz>len(data)-off):
            split=True
        # Pinned qcom_mdt_read_metadata checks flags on every phdr from index 1,
        # including PT_NULL hash descriptors (stock Motorola images use them).
        if i >= 1 and (flags & TYPE_MASK)==TYPE_HASH:
            has_hash.append(i)
        loadable=(typ==PT_LOAD and (flags & TYPE_MASK)!=TYPE_HASH and memsz!=0)
        if loadable:
            if filesz>memsz:
                raise ValueError(f"{filename}: segment {i} filesz>memsz")
            lo=min(lo,paddr)
            hi=max(hi,(paddr+memsz+4095)&~4095)
            if flags & RELOCATABLE:
                reloc=True
        segments.append({
            "index":i,"p_type":typ,"p_offset":off,
            "p_vaddr":vaddr,"p_paddr":paddr,
            "p_filesz":filesz,"p_memsz":memsz,
            "p_flags_hex":f"0x{flags:x}",
            "p_align":alignment,"hash_segment":i in has_hash,
            "loadable_under_qcom_mdt":loadable,
            "in_source_image":not filesz or (off<=len(data) and filesz<=len(data)-off)})
    if lo>=hi:
        raise ValueError("no loadable segments")
    return {
        "filename":filename,"sha256":sha(data),"size":len(data),
        "elf_header_size":struct.unpack_from("<H",data,40)[0],
        "program_headers":segments,"program_header_count":count,
        "firmware_loader_split_detection":split,
        "firmware_loader_relocatable":reloc,
        "qcom_mdt_get_size_bytes":hi-lo,
        "qcom_mdt_paddr_min":lo,"qcom_mdt_paddr_max_aligned_exclusive":hi,
        "hash_segment_indices":has_hash
    }


def segment_requirements(record, image, directory):
    source = record["filename"]
    split = record["firmware_loader_split_detection"]
    base = source[:-3]
    required=[]
    for h in record["program_headers"]:
        if not h["loadable_under_qcom_mdt"] or not h["p_filesz"]:
            continue
        if not split:
            required.append({"index":h["index"],"source":"in_single_MBN",
                             "bytes":h["p_filesz"],
                             "file_offset":h["p_offset"],
                             "within_image":h["in_source_image"]})
        else:
            name=base + "b%02d"%h["index"]
            data=extract(image,name,directory/name)
            required.append({"index":h["index"],"source":"split_segment",
                             "filename":name,"expected_bytes":h["p_filesz"],
                             "actual_bytes":len(data),"sha256":sha(data),
                             "exact_size_matches":len(data)==h["p_filesz"]})
    hashes=[]
    if record["program_header_count"]<2 or record["program_headers"][0]["p_type"]==PT_LOAD:
        raise ValueError(source+": qcom_mdt_read_metadata requires leading non PT_LOAD header")
    if not record["hash_segment_indices"]:
        raise ValueError(source+": no Qualcomm TYPE_HASH program header")
    for i in record["hash_segment_indices"]:
        ph=record["program_headers"][i]
        hdr_bytes=record["program_headers"][0]["p_filesz"]
        hash_len=ph["p_filesz"]
        if hdr_bytes + hash_len == record["size"]:
            placement="packed_directly_after_ELF_header"
        elif ph["in_source_image"]:
            placement="in_ELF_at_phdr_offset"
        else:
            placement="split_bXX_required"
        extra={"phdr_index":i,"size":hash_len,"placement":placement}
        if placement=="split_bXX_required":
            name=base+"b%02d"%i
            data=extract(image,name,directory/name)
            extra["split_filename"]=name
            extra["split_sha256"]=sha(data)
            extra["split_size_matches"]=len(data)==hash_len
        hashes.append(extra)
    return required,hashes


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--json-out",required=True,type=pathlib.Path)
    args=a.parse_args()
    base=pathlib.Path(__file__).parent
    ranges=mod(base/"inspect-oneli-stock-ranges.py","zipranges")
    radio_parser=mod(base/"inspect-oneli-moto-radio.py","radioparse")
    ranges.TARGETS=("radio.img",)
    ranges.COMPRESSED_CAP=145*1024*1024
    ranges.EXPANDED_CAP=230*1024*1024
    listing,_=ranges.metadata(ranges.STOCK_URL)
    radio=ranges.member(ranges.STOCK_URL,"radio.img",listing["radio.img"])
    if sha(radio)!=RADIO_HASH:
        raise ValueError("radio image differs from pinned reference")
    parsed=radio_parser.parse_single_lonely(radio)
    if parsed is None:
        raise ValueError("expected Motorola SINGLE_N_LONELY")
    _,members=parsed
    non_hlos=next((memoryview(radio)[off:off+size]
                   for name,off,size in members if name=="NON-HLOS.bin"),None)
    if non_hlos is None or sha(non_hlos)!=NONHLOS_HASH:
        raise ValueError("NON-HLOS member mismatch")
    with tempfile.TemporaryDirectory() as temp:
        root=pathlib.Path(temp)
        img=root/"non-hlos-ext4.img"
        meta=radio_parser.decode_android_sparse(non_hlos,img)
        if meta["decoded_sha256"]!=EXT4_HASH:
            raise ValueError("decoded ext4 image SHA mismatch")
        results=[]
        for filename in EXPECTED:
            buf=extract(img,filename,root/filename)
            if sha(buf)!=EXPECTED[filename]:
                raise ValueError("firmware source file hash mismatch")
            entry=inspect_elf(buf,filename)
            required,hashes=segment_requirements(entry,img,root)
            entry["segments_needed_at_runtime"]=required
            entry["pas_metadata_hash_segment_placement"]=hashes
            entry["expected_reserved_region_bytes"]=RESERVED[
                filename.split(".")[0]]
            entry["would_fit_reserved_region_by_size"]=(
                entry["qcom_mdt_get_size_bytes"]<=entry["expected_reserved_region_bytes"])
            if any(x.get("exact_size_matches") is False for x in required):
                raise ValueError("split load segment differs from ELF expected size")
            if any(x.get("split_size_matches") is False for x in hashes):
                raise ValueError("split hash segment differs from expected size")
            results.append(entry)
            print(filename,"ELF phdr",entry["program_header_count"],
                  "split",entry["firmware_loader_split_detection"],
                  "MDT size",entry["qcom_mdt_get_size_bytes"],flush=True)
    result={"source_zip_sha256_prior_full_download":ZIP_HASH,
            "radio_sha256":RADIO_HASH,"non_hlos_sha256":NONHLOS_HASH,
            "decoded_ext4_sha256":EXT4_HASH,
            "loader_source_pin":"Drzet/linux:razr/vpu at 869cf4a6ad21afcc2435c4e2d1d4fa9ab33fb4bf",
            "scope":"host_structure_only_no_firmware_binary_or_secure_authorization",
            "qcom_mdt_rules":["PT_LOAD excluding QCOM_MDT_TYPE_HASH and memsz 0",
                              "split if any nonzero phdr p_offset+p_filesz is beyond ELF file length",
                              "split segment name is basename.b%02d using ORIGINAL phdr index",
                              "relocatable if any loadable flags has BIT(27)"],
            "files":results}
    args.json_out.parent.mkdir(parents=True,exist_ok=True)
    args.json_out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("Wrote structural signed loader manifest",args.json_out.stat().st_size,flush=True)

if __name__=="__main__":
    main()
