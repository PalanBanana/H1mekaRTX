# BAR/MMIO Risk Ledger

## Purpose

Stage 5 records the current BAR/MMIO safety boundary before any future low-level research.

This document exists to prevent accidental escalation from read-only PCI inventory work into unsafe PCI config-space writes, MMIO access, GPU reset logic, firmware loading, display initialization, framebuffer initialization, or Metal acceleration attempts.

## Current Stage

Current allowed scope:

- Read Stage 3 diagnostics output
- Read Stage 4 normalized summary JSON
- Validate that the summary still declares the project as read-only
- Document unknowns and blockers
- Generate safety reports from local JSON files

Current forbidden scope:

- PCI config-space writes
- MMIO writes
- BAR memory poking
- GPU reset logic
- GSP initialization
- firmware loading
- display engine initialization
- framebuffer initialization
- Metal acceleration attempts
- DriverKit activation

## RTX 5070 PCI Target

| Field | Value |
| --- | --- |
| Vendor ID | `0x10de` |
| Device ID | `0x2f04` |
| IOPCIMatch | `0x2f0410de` |
| Subsystem Vendor ID | `0x1458` |
| Subsystem ID | `0x417e` |

## Risk Ledger

| Area | Current State | Risk | Required Before Escalation |
| --- | --- | --- | --- |
| BAR identity | OS-visible hints collected only | BAR numbers, size meanings, and aperture roles may be misread | Confirm BAR layout from reliable documentation or safe read-only APIs |
| MMIO semantics | Unknown | Writing unknown registers can hang, reset, or wedge the GPU/system | Build a documented register map before any access |
| PCI config-space writes | Forbidden | Incorrect writes can break device enumeration or routing | Define a zero-write policy and review any future exception separately |
| GPU reset path | Unknown and forbidden | Bad reset sequencing can leave the device unusable until reboot or power cycle | Document reset prerequisites and recovery path first |
| GSP / firmware path | Unknown and forbidden | Incorrect firmware loading can fail unpredictably or destabilize the device | Keep firmware handling out of scope until a later explicit stage |
| Display engine | Unknown and forbidden | Display init can affect outputs, scanout, and framebuffer ownership | Do not initialize display hardware in BAR research stages |
| Framebuffer | Unknown and forbidden | Incorrect framebuffer assumptions can corrupt display state | Keep framebuffer work separate from BAR inventory work |
| Metal acceleration | Not attempted | Metal requires much more than PCI visibility | Treat Metal as a later high-level milestone, not a BAR diagnostics stage |
| DriverKit activation | Not enabled in this stage | Device ownership and aperture access change the safety profile | Require a separate activation design and review |

## Safety Boundary Checker

Script:

    ./scripts/check-bar-safety-boundary.py ~/Desktop/H1mekaRTX-bar-inventory-test/bar-inventory-summary.json

With Markdown output:

    ./scripts/check-bar-safety-boundary.py ~/Desktop/H1mekaRTX-bar-inventory-test/bar-inventory-summary.json --out-dir ~/Desktop/H1mekaRTX-bar-inventory-test

Expected output file:

    bar-mmio-safety-check.md

## Pass Criteria

The checker should pass only when:

- summary schema is `h1mekartx.bar_inventory_summary.v1`
- RTX 5070 target IDs match the expected values
- `safety_boundary.read_only` is `true`
- all risky action flags are `false`
- vendor ID `0x10de` is present in the target hits
- either device ID `0x2f04` or IOPCIMatch `0x2f0410de` is present in the target hits

## Notes

This stage is not a driver activation stage.

This stage does not request exclusive PCI device access.

This stage does not map or write any BAR memory.

This stage only validates that previous inventory outputs still describe a read-only safety boundary.
