# Sonoma Install Success Notes

## Result

macOS Sonoma successfully booted on the target test system using OpenCore.

## macOS

- Product Version: macOS 14.8.7
- Build Version: 23J520
- SMBIOS: iMacPro1,1

## Hardware

- CPU: Intel Core i7-14700K
- Memory: 32 GB
- GPU target: NVIDIA GeForce RTX 5070
- Motherboard: ASRock B760M-PRO-A

## RTX 5070 PCI Visibility

The RTX 5070 is visible to macOS as a PCI device.

Observed values:

- Type: VGA-Compatible Controller
- Bus: PCI
- Slot: Slot-1
- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- Subsystem Vendor ID: `0x1458`
- Subsystem ID: `0x417e`
- Revision ID: `0x00a1`
- Link Width: `x16`

## NVIDIA Audio Function

An additional NVIDIA PCI function is visible:

- IORegistry name: `pci10de,2f80@0,1`
- IOName: `pci10de,2f80`
- Class: `pciclass,040300`

## Notes

This confirms Stage 1 PCI visibility for H1mekaRTXProbe.

This does not indicate graphics acceleration, framebuffer support, Metal support, GSP initialization, or display engine support.

Raw logs are kept privately and are not committed to the repository.
