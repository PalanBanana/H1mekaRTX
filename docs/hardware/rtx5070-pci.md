# RTX 5070 PCI Information

## Device

- GPU: NVIDIA GB205 GeForce RTX 5070
- PCI address: 01:00.0
- Vendor ID: 0x10de
- Device ID: 0x2f04
- Revision ID: 0xa1
- Class code: 0x030000
- Subsystem Vendor ID: 0x1458
- Subsystem Device ID: 0x417e

## Notes

This device is the primary target for Stage 1: H1mekaRTXProbe.

Stage 1 will only attempt PCI device detection and read-only BAR/config-space inspection.
No MMIO writes, VRAM writes, display initialization, GSP initialization, or Metal registration will be attempted.
