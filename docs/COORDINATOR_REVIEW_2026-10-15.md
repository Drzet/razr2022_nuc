# Coordinator review — MBM research, VPU assumptions and USB identity
Date: 2026-10-15. This decision supersedes conflicting pauses/identity prerequisites in earlier dated reviews. Current assignments remain in [NEXT_TASKS](NEXT_TASKS.md).

## MBM research disposition

Reviewed research/oneli-mbm-readonly-20261015 at [5a8d6ab606c825dbe776db43955c44214f7c64e3](https://github.com/Drzet/razr2022_nuc/commit/5a8d6ab606c825dbe776db43955c44214f7c64e3), including both reports, placement/literal extraction scripts and successful job metadata. Inspected the actual constants job116677819664/run38809199858 output at source8c7e5e2; its member/PE hashes and four numeric literals match the report. No firmware acquisition, independent disassembly rerun or handset execution was performed. The complete disassembly artifact was not independently re-decoded in this review; branch analysis is attributed research evidence, not newly reproduced instruction-level proof.

Accept the [static address contract](https://github.com/Drzet/razr2022_nuc/blob/5a8d6ab606c825dbe776db43955c44214f7c64e3/docs/oneli_mbm_kernel_load_address_contract_2026-10-15.md) for planning. The earlier generic statement that loader placement is wholly unknown is superseded:
- Successful UEFI-variable route for the accepted uncompressed Image: K=B+text_offset+O; E=B+Z+O. Its text_offset is zero.
- Reported 64-bit fallback: K=(M|0x80000)+O; E=M+0x06400000+O. Preserve bitwise OR; do not silently replace it with addition for arbitrary M.
- initrd=E-align_up(R,P)-P; DTB=initrd-S-P. ABL's reported DTB>K check is weaker than DTB>=K+Image.image_size.
- Independently checked arithmetic: required separation with default S=2MiB/P=4096 is 55,320,576 bytes plus page-rounded R. Aligned-M fallback capacity leaves 0x02ebe000 bytes for rounded ramdisks. This is capacity arithmetic, not an observed allocation.
- With aligned M and O=0, fallback adds 0x80000 to a text_offset=0 Image: it fails the stated 2MiB entry alignment. Capacity does not resolve alignment. Record selected path, K/E/O, RAM/carveouts and final FDT before declaring a native artifact ready.
- Downloaded fastboot-boot support and its lock guard are source findings. Selected DT/DTBO, vendor/generic ramdisk composition, RAM fixup and observable output remain trial questions. Unlock and successful kernel entry are not prerequisites to offline planning.

**Concrete research defect, nonblocking to numeric constants:** constants-script cstr searches for an unaligned double-zero byte pair. For UTF-16LE ASCII it trims the last character; the real job prints KernelBaseAdd and KernelSiz. Coordinator reproduced this on synthetic KernelBaseAddr bytes. Correct by scanning aligned 16-bit code units for zero and test both names. Do not cite this faulty field as exact spelling proof. Also validate RVA-to-file mapping for the literal sections; the placement script currently verifies identity mapping only for .text. Reuse saved metadata/artifacts; no new firmware retrieval is needed to plan or correct the decoder. The older actual-code report's “full relocation call graph” request is superseded by the later scoped contract, except specifically identified missing paths.

## VPU decision

Verified current canonical heads remain project0c50bf141dbb2a96cd19e79eb35e27bb1e807a63 / kernel7ac8d3afedfde74286b52e11aaa1eca42a1329a5. No newer VPU delta was present. Reuse the completed [calculator review](VPU_REVIEW_2026-10-13.md#checked-calculator-review--2026-10-15-evening), including independently reproduced1362 vectors/3157 assertions; do not repeat unchanged tests.

The user explicitly confirms acceptance of the VPU hardware assumption. Record the outstanding clock consumer division-by-three as **[INFERRED, USER-ACCEPTED FOR DEVELOPMENT]**, and retain the accepted four-pipe/no-cache-discount model. Missing physical divider confirmation is no longer an offline development prerequisite. This is permission to develop using the assumption, not measured clock/cache behavior. Linux clock rounding/provider behavior still must be handled correctly in implementation.

Activate a bounded consumer-policy contract using the reviewed calculator: rate/startup semantics, admission and checked-error handling, raw D/L versus route limits, disjoint ICC aggregation and clock rates. Reject unsupported/unrepresentable or over-cap configurations rather than silently presenting a capped vote as sufficient. Specify failure propagation and vote rollback before wiring. No new empirical tuning search or unchanged arithmetic replay. Native PAS/HFI/DMA tests and the demonstrated inherited IOVA failure behavior remain separate; assumption acceptance does not fix a source defect.

## USB decision

Accept project481c399cee777014586b083f0305614e09aa9c68 and kernel1e5268277f6d4c25cde2f3e2b3f00439107e087a for isolated source/host scope. Inspected the full two-commit diff from61202a82: driver policy d87632e and binding-description correction1e526827. Unknown readable IDs warn with raw ID/revision and continue only in the existing oneli profile. All read errors remain fatal before tuning; cleanup/lifecycle behavior is unchanged. No invented BUK identifier or global bypass.

Coordinator independently executed the submitted production-provider harness: **44 scenarios PASS**, ASan/UBSan with leak detection disabled. Source SHA2562130a965f1f31d340e8279d64515979c8813664e906f77a92730487b4cb5827f and harness SHA2561f64d7a846ebe468b864f23052ad864c0fff4f2d1c22f961662fa8d78c7ba15e match the evidence. Inspected owner-produced object/MODPOST/module-link log; no independent ARM64 rebuild or binary hash verification. Binding constraints are unchanged; prior schema evidence reused.

BUK ID capture is useful diagnostic evidence, **not an allowlist prerequisite**. Active-low PM8350C GPIO7 descriptor proposal is accepted at source-contract level; actual provider labels/ownership and L2B voltage range/rounding remain board-integration work. USB pauses after this accepted delivery.

## Boot receipt and next step

Reviewed Boot handoff812172869a8c9665c6a39004aad9b1c52cf036bf and its pinned board-contract reference. Its GPIO26/27 qup7 observation demonstrates no functional mux mismatch merely from reversed TX/RX label names. The grouped parent proposal distinguishes PM8350/PM8350C/PM8450 and variable B_PLUS. Retain as source proposal; no provider instantiation or electrical acceptance is implied. Next Boot task incorporates MBM findings into the existing readiness record and resolves only the named evidence-tool defects; no packaging replay.

Accepted integration remains2b5acf108ae37040ac1e652e029bb37f5609e886. No kernel merge, shared DTS enablement, native trial or new combined build is selected by this review.
