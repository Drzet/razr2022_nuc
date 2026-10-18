#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Audit actual Linux olddefconfig output; never pretend to resolve Kconfig here."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re

SOURCE = '7f3865ee17c37146e183a45cd8ff2b6c59d0e9ce'
ACCEPTED_SHA = 'e10f77e9c982a4c3c81c94e69922ad8ae623b71e99df88e40c415e5a6fc0b273'
# Original accepted feature choices, plus current native UART/pstore,
# QEMU virt + Debian/systemd, signed regdb, and USB/DP diagnostic needs.
BUILTINS = '''ARCH_QCOM ARCH_VEXPRESS ARM64 64BIT OF MODULES MODULE_UNLOAD
 BLK_DEV_INITRD RD_GZIP DEVTMPFS DEVTMPFS_MOUNT TMPFS PROC_FS SYSFS
 BINFMT_ELF EXT4_FS CGROUPS NAMESPACES USER_NS SECCOMP SECCOMP_FILTER
 FHANDLE INOTIFY_USER EPOLL FUTEX UNIX INET NET IPV6 KEYS CRYPTO_SHA256
 ARM_GIC_V3 ARM_PSCI_FW SERIAL_AMBA_PL011 SERIAL_AMBA_PL011_CONSOLE
 VIRTIO VIRTIO_MMIO VIRTIO_PCI VIRTIO_BLK VIRTIO_NET VIRTIO_CONSOLE
 PRINTK SERIAL_EARLYCON SERIAL_QCOM_GENI SERIAL_QCOM_GENI_CONSOLE PSTORE
 FW_LOADER REGULATOR REGULATOR_QCOM_RPMH POWER_SEQUENCING
 POWER_SEQUENCING_QCOM_WCN PCIE_QCOM PHY_QCOM_QMP PHY_QCOM_QMP_PCIE
 PCI_PWRCTRL_GENERIC BT_LE BT_HCIUART_SERDEV BT_HCIUART_QCA
 CFG80211_REQUIRE_SIGNED_REGDB CFG80211_USE_KERNEL_REGDB_KEYS
 USB USB_DWC3 USB_DWC3_QCOM USB_ROLE_SWITCH USB_XHCI_HCD
 USB_XHCI_PLATFORM USB_STORAGE USB_GADGET DRM_DISPLAY_DP_HELPER'''
MODULES = '''PSTORE_RAM PCI_PWRCTRL_PWRSEQ CFG80211 MAC80211 ATH11K
 ATH11K_PCI MHI_BUS QRTR QRTR_MHI BT BT_HCIUART BT_QCA TYPEC
 PHY_NXP_PTN3222 PHY_SNPS_EUSB2 DRM_MSM'''
REQUIRED = {f'CONFIG_{n}': v for v, names in [('y', BUILTINS), ('m', MODULES)]
            for n in names.split()}
# Preserve all accepted oneli platform and radio/diagnostic helpers,
# without freezing clearly foreign SOC-specific board drivers.
PREFIXES = ( 'CONFIG_QCOM_', 'CONFIG_PINCTRL_QCOM', 'CONFIG_PHY_QCOM',
 'CONFIG_REGULATOR_QCOM', 'CONFIG_SND_SOC_QCOM', 'CONFIG_ATH11K',
 'CONFIG_CFG80211', 'CONFIG_MAC80211', 'CONFIG_BT_HCIUART',
 'CONFIG_BT_LE', 'CONFIG_BT_QCA', 'CONFIG_MHI_', 'CONFIG_QRTR',
 'CONFIG_VIRTIO', 'CONFIG_PSTORE', 'CONFIG_SERIAL_QCOM_GENI',
 'CONFIG_SERIAL_AMBA_PL011', 'CONFIG_DRM_MSM', 'CONFIG_DRM_DISPLAY_DP',
 'CONFIG_USB_DWC3_QCOM', 'CONFIG_USB_CONFIGFS', 'CONFIG_USB_F_',
 'CONFIG_USB_NET_', 'CONFIG_USB_ROLE_SWITCH', 'CONFIG_TYPEC',
 'CONFIG_UCSI_', 'CONFIG_PCIE_QCOM', 'CONFIG_PCI_PWRCTRL',
 'CONFIG_PHY_NXP_PTN3222', 'CONFIG_PHY_SNPS_EUSB2')


def config(path):
    result = {}
    for line in path.read_text().splitlines():
        m = re.fullmatch(r'(CONFIG_\w+)=(.+)', line)
        if m:
            result[m[1]] = m[2]
        else:
            m = re.fullmatch(r'# (CONFIG_\w+) is not set', line)
            if m:
                result[m[1]] = 'n'
    return result


def demand(actual, expected, label):
    bad = {k: [v, actual.get(k, 'ABSENT')] for k, v in expected.items()
           if actual.get(k) != v}
    if bad:
        raise AssertionError(f'{label}: {json.dumps(bad, sort_keys=True)}')


def main():
    p = argparse.ArgumentParser()
    for key in ('accepted', 'candidate', 'radio-fragment', 'qemu-fragment',
                'reductions', 'evidence'):
        p.add_argument('--' + key, required=True, type=Path)
    a = p.parse_args()
    a.evidence.mkdir(parents=True, exist_ok=True)
    assert hashlib.sha256(a.accepted.read_bytes()).hexdigest() == ACCEPTED_SHA
    old, new = config(a.accepted), config(a.candidate)
    exclusions = config(a.reductions)
    assert len(exclusions) > 20 and all(v == 'n' for v in exclusions.values())
    assert all(old.get(k) in ('y', 'm') for k in exclusions)
    assert not {'CONFIG_ARCH_QCOM', 'CONFIG_ARCH_VEXPRESS'} & exclusions.keys()
    demand(old, REQUIRED, 'accepted baseline')
    demand(new, REQUIRED, 'resolved functional contract')
    radio = {k: v for k, v in config(a.radio_fragment).items() if v in ('y', 'm')}
    demand(new, radio, 'accepted kernel radio fragment')
    qemu = config(a.qemu_fragment)
    assert qemu['CONFIG_DUMMY'] == 'm'
    demand(new, {k: v for k, v in qemu.items() if v == 'y'}, 'QEMU virt built-ins')
    # DUMMY=m belongs to an older QEMU fragment; current accepted Userspace
    # tests hci_uart and explicitly notes CONFIG_DUMMY is absent.
    frozen = {k: v for k, v in old.items() if v in ('y', 'm')
              and k.startswith(PREFIXES)}
    demand(new, frozen, 'preserve oneli and generic diagnostic consumers')
    demand(new, exclusions, 'requested foreign platforms removed')
    before = {k: v for k, v in old.items() if v in ('y', 'm')}
    after = {k: v for k, v in new.items() if v in ('y', 'm')}
    removed = sorted(before.keys() - after.keys())
    added = sorted(after.keys() - before.keys())
    changed = sorted(k for k in before.keys() & after.keys() if before[k] != after[k])
    assert len(removed) >= len(exclusions), 'ineffective reduction'
    counts = {name: {v: sum(x == v for x in cfg.values()) for v in ('y','m')}
              for name, cfg in [('accepted', before), ('candidate', after)]}
    for group in counts.values():
        group['enabled_total'] = group['y'] + group['m']
    result = {'status': 'RESOLVED_CONFIG_ONLY_NO_BUILD',
              'pinned_kernel': SOURCE, 'accepted_sha256': ACCEPTED_SHA,
              'candidate_sha256': hashlib.sha256(a.candidate.read_bytes()).hexdigest(),
              'counts': counts, 'requested_platform_disables': len(exclusions),
              'removed_enabled': len(removed), 'new_enabled': len(added),
              'changed_y_m': len(changed), 'strict_required': len(REQUIRED),
              'retained_accepted_consumer_symbols': len(frozen),
              'radio_fragment_checked': len(radio),
              'qemu_builtin_checked': sum(v == 'y' for v in qemu.values()),
              'historical_DUMMY_m_exception': 'accepted Userspace tests hci_uart',
              'image_dtb_modules_qemu_run': False}
    for path, lines in [('removed-enabled.txt', removed), ('new-enabled.txt', added),
                        ('changed-y-m.txt', [f'{k} {before[k]} -> {after[k]}' for k in changed]),
                        ('required-contract.txt', [f'{k}={v}' for k,v in sorted(REQUIRED.items())])]:
        (a.evidence / path).write_text('\n'.join(lines) + '\n')
    (a.evidence / 'before-after.diff').write_text(''.join(difflib.unified_diff(
        a.accepted.read_text().splitlines(keepends=True),
        a.candidate.read_text().splitlines(keepends=True),
        fromfile='accepted.config', tofile='resolved-reduced.config')))
    (a.evidence / 'report.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('ONELI_REDUCED_CONFIG_CONTRACT_PASS '+json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
