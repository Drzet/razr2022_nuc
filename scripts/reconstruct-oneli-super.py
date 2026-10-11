#!/usr/bin/env python3
"""Format-aware, bounded reconstruction of multi-file Android sparse super.

Input: Motorola stock ZIP. Each .img_sparsechunk member is parsed as an
independent Android sparse stream; DONT_CARE seeks in the SAME output image.
This is NOT concatenation of the chunks' compressed or expanded bytes.
No stock bytes are copied to the output JSON manifest.
"""
import argparse
import hashlib
import json
import os
import re
import struct
import zipfile
from pathlib import Path

SPARSE_MAGIC = 0xED26FF3A
RAW, FILL, SKIP, CRC = 0xCAC1, 0xCAC2, 0xCAC3, 0xCAC4
MAX_VIRTUAL = 32 * 1024**3
MAX_CHUNKS = 1_000_000


def exactly(stream, n):
    result = stream.read(n)
    if len(result) != n:
        raise ValueError(f"truncated sparse stream: needed {n}, got {len(result)}")
    return result


def reconstruct(archive, output, report):
    with zipfile.ZipFile(archive) as zf, output.open("w+b") as raw:
        names = [x.filename for x in zf.infolist() if re.fullmatch(r"super\.img_sparsechunk\.\d+", x.filename)]
        names.sort(key=lambda x: int(x.rsplit(".", 1)[1]))
        if not names or [int(x.rsplit(".", 1)[1]) for x in names] != list(range(len(names))):
            raise ValueError("missing or non-contiguous super sparsechunk members")
        if len(names) > 128:
            raise ValueError("unreasonable sparse member count")
        report["sparse_members"] = []
        virtual_max = 0
        for name in names:
            member = zf.getinfo(name)
            with zf.open(member, "r") as stream:
                header = struct.unpack("<I4H4I", exactly(stream, 28))
                magic, major, minor, header_size, chunk_header_size, block_size, total_blocks, chunk_count, checksum = header
                if (magic != SPARSE_MAGIC or major != 1 or header_size < 28
                        or chunk_header_size < 12 or block_size < 512
                        or block_size > 65536 or block_size % 512
                        or chunk_count > MAX_CHUNKS or total_blocks * block_size > MAX_VIRTUAL):
                    raise ValueError(f"{name}: invalid Android sparse header {header}")
                if header_size > 28:
                    exactly(stream, header_size - 28)
                raw.seek(0)
                logical_blocks = 0
                byte_counters = {"raw": 0, "fill": 0, "skip": 0}
                for _ in range(chunk_count):
                    kind, reserved, blocks, size = struct.unpack("<2H2I", exactly(stream, 12))
                    if chunk_header_size > 12:
                        exactly(stream, chunk_header_size - 12)
                    span = blocks * block_size
                    if span > MAX_VIRTUAL or logical_blocks + blocks > total_blocks:
                        raise ValueError(f"{name}: output span exceeds sparse header")
                    if kind == RAW:
                        if size != chunk_header_size + span:
                            raise ValueError(f"{name}: bad RAW chunk length")
                        todo = span
                        while todo:
                            buf = exactly(stream, min(todo, 1024*1024))
                            raw.write(buf)
                            todo -= len(buf)
                        byte_counters["raw"] += span
                    elif kind == FILL:
                        if size != chunk_header_size + 4:
                            raise ValueError(f"{name}: bad FILL chunk length")
                        pattern = exactly(stream, 4)
                        tile = (pattern * (1024*1024 // 4))
                        todo = span
                        while todo:
                            n = min(todo, len(tile))
                            raw.write(tile[:n])
                            todo -= n
                        byte_counters["fill"] += span
                    elif kind == SKIP:
                        if size != chunk_header_size:
                            raise ValueError(f"{name}: bad DONT_CARE chunk length")
                        raw.seek(span, os.SEEK_CUR)
                        byte_counters["skip"] += span
                    elif kind == CRC:
                        if blocks != 0 or size != chunk_header_size + 4:
                            raise ValueError(f"{name}: bad CRC32 chunk length")
                        exactly(stream, 4)
                    else:
                        raise ValueError(f"{name}: unsupported chunk type {kind:#x}")
                    logical_blocks += blocks
                if logical_blocks != total_blocks:
                    raise ValueError(f"{name}: output block count mismatches header")
                # Require that ZipExtFile has consumed and CRC-checked the entire member.
                if stream.read(1):
                    raise ValueError(f"{name}: trailing payload beyond declared Android sparse chunks")
                virtual_max = max(virtual_max, total_blocks * block_size)
                report["sparse_members"].append({
                    "zip_member": name,
                    "member_uncompressed_bytes": member.file_size,
                    "zip_crc32": f"{member.CRC:08x}",
                    "sparse_header": {"major": major, "minor": minor, "block_bytes": block_size,
                                      "total_blocks": total_blocks, "chunk_count": chunk_count,
                                      "header_crc32": f"{checksum:08x}"},
                    "logical_output_bytes": total_blocks * block_size,
                    "chunk_data_bytes": byte_counters})
                print(f"reconstructed {name}: {chunk_count} typed chunks, virtual {total_blocks*block_size}")
        raw.truncate(virtual_max)
        raw.flush()
        os.fsync(raw.fileno())
        report["raw_super"] = {
            "virtual_bytes": virtual_max,
            "allocated_bytes": output.stat().st_blocks * 512,
            "first_4k_sha256": hashlib.sha256(output.open("rb").read(4096)).hexdigest(),
        }
        raw.seek(4096)
        report["raw_super"]["has_android_lp_geometry_magic_at_4096"] = raw.read(4) == b"gDla"
        if not report["raw_super"]["has_android_lp_geometry_magic_at_4096"]:
            raise ValueError("super logical partition geometry magic missing at 4096 after reconstruction")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stock-zip", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--json-out", type=Path, required=True)
    a = p.parse_args()
    report = {"parser": "Android sparse v1, 4 supported chunk kinds", "input_zip": a.stock_zip.name,
              "stock_version": "U2SLS34.1-42-14-11", "runtime_hardware_tested": False}
    reconstruct(a.stock_zip, a.output, report)
    a.json_out.parent.mkdir(parents=True, exist_ok=True)
    a.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
