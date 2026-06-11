# H1mekaRTX

<!-- H1mekaRTX:ci-badges:start -->
[![BAR Safety Gates](https://github.com/PalanBanana/H1mekaRTX/actions/workflows/bar-safety-gates.yml/badge.svg?branch=main)](https://github.com/PalanBanana/H1mekaRTX/actions/workflows/bar-safety-gates.yml)
<!-- H1mekaRTX:ci-badges:end -->

H1mekaRTX is an experimental research project for NVIDIA GeForce RTX 5070 detection, compute-only runtime research, framebuffer-only output research, and long-term Metal acceleration research on macOS.

> Status: research-only. This repo does **not** provide working macOS NVIDIA graphics acceleration, CUDA support, or a production display driver.

## Target GPU

- GPU: NVIDIA GB205 / GeForce RTX 5070
- Board: Gigabyte GV-N5070WF3OC-12GD/F1/115C
- PCI address in dump: `01:00.0`
- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- Subsystem: `0x1458:0x417e`
- Revision: `0xa1`
- Class: `0x030000` VGA controller
- VBIOS SHA-256: `72111ab06a2b02609099a65c59c5031193dd411ec31caff920103bfb073993b5`

## Roadmap

### Stage 1 — H1mekaRTXProbe

Goal: detect RTX 5070 from macOS through DriverKit/PCIDriverKit and print PCI config/BAR metadata.

Success criteria:

- Match PCI device `10de:2f04`.
- Read vendor/device/subsystem/revision/class values.
- Read BAR0/BAR1/BAR3/BAR5 metadata.
- Show `H1mekaRTXProbe` in IORegistry.
- Do **not** write to MMIO/VRAM in Stage 1.

### Stage 2 — H1mekaRTXCompute

Goal: research compute-only runtime paths using Linux/Nouveau/GSP behavior as reference.

Success criteria:

- Understand GSP initialization and BAR0 usage.
- Research memory objects, channels, fences, copy engine behavior.
- Run a tiny proof-of-concept command only after safe low-level understanding.

### Stage 3 — H1mekaRTXFramebuffer

Goal: research framebuffer-only output without Metal acceleration.

Success criteria:

- Parse VBIOS/DCB-related data.
- Understand connector/EDID/mode-setting path.
- Eventually display a solid color or checkerboard pattern.

### Stage 4 — H1mekaRTXMetalResearch

Goal: long-term feasibility research for Metal-compatible acceleration.

This is not a near-term implementation target.

## Repository layout

```text
H1mekaRTX/
├─ docs/
│  ├─ hardware/
│  ├─ macos/
│  ├─ nvidia/
│  └─ framebuffer/
├─ dumps/
│  └─ rtx5070-gigabyte-windforce-oc-12g/
├─ src/
│  ├─ H1mekaRTXProbe/
│  ├─ H1mekaRTXCompute/
│  └─ H1mekaRTXFramebuffer/
└─ tools/
   ├─ linux/
   ├─ macos/
   └─ common/
```

## Safety rules

- Stage 1 must be read-only.
- Do not write to BAR0/BAR1/BAR3 until the register map and reset path are understood.
- Do not ship this as a functional display driver.
- Keep raw dumps separated from source code.

## Current next task

Implement the Stage 1 DriverKit/PCIDriverKit probe skeleton and test whether macOS can match `10de:2f04`.
