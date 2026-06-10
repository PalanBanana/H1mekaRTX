\# Hackintosh Test Plan for H1mekaRTXProbe



This document tracks the planned Hackintosh test environment for H1mekaRTXProbe.



\## Purpose



The Hackintosh environment is not intended for daily macOS usage or graphics acceleration.



Its only Stage 1 purpose is:



\- boot macOS on the target PC

\- load H1mekaRTXProbe

\- match the RTX 5070 PCI device

\- verify IORegistry visibility

\- collect DriverKit logs

\- confirm PCI IDs and BAR enumeration



\## Target Hardware



\- CPU: Intel Core i7-14700K

\- GPU: NVIDIA GeForce RTX 5070

\- iGPU: Intel UHD Graphics 770

\- Motherboard: ASRock B760M-PRO-A

\- Memory: 32 GB

\- Storage: MSI NVMe M450 1 TB



\## Known Limitations



\- RTX 5070 has no native macOS graphics acceleration target in Stage 1.

\- Intel UHD 770 is not the target display device.

\- Stage 1 does not attempt Metal acceleration.

\- Stage 1 does not attempt framebuffer output.

\- Stage 1 does not attempt GSP initialization.



\## Stage 1 Test Scope



Allowed:



\- boot macOS

\- inspect IORegistry

\- activate DriverKit dext

\- read PCI config space

\- enumerate BARs

\- collect logs



Forbidden:



\- MMIO writes

\- VRAM writes

\- firmware upload

\- display engine programming

\- GSP initialization

\- Metal registration



\## Success Criteria



\- macOS boots far enough to run terminal commands

\- H1mekaRTXProbe can be installed or activated

\- RTX 5070 matches Vendor ID `0x10de` and Device ID `0x2f04`

\- logs show PCI identifiers

\- logs show BAR0/BAR1/BAR3/BAR5 information

