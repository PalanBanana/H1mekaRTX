# Stage 3 Framebuffer-only Plan

## Goal

Research a non-Metal, framebuffer-only output path for RTX 5070 on macOS.

## First success target

```text
Parse VBIOS
→ identify connector/display data
→ read EDID/mode data path
→ allocate scanout-like buffer
→ eventually draw solid color/checkerboard
```

## Required data already collected

- VBIOS ROM: `162,304` bytes
- BAR0 MMIO region
- BAR1 16GB aperture
- Nouveau framebuffer evidence from Linux: `nouveaudrmfb fb0`

## Warning

This stage requires display engine knowledge. Do not write display registers until recovery/reset behavior is understood.
