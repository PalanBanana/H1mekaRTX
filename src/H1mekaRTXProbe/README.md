\# H1mekaRTXProbe



H1mekaRTXProbe is a planned read-only macOS DriverKit/PCIDriverKit probe driver for NVIDIA RTX 5070.



\## Target Device



\- GPU: NVIDIA GB205 GeForce RTX 5070

\- Vendor ID: 0x10de

\- Device ID: 0x2f04

\- Subsystem Vendor ID: 0x1458

\- Subsystem Device ID: 0x417e

\- Revision ID: 0xa1

\- Class Code: 0x030000



\## Stage 1 Scope



Allowed:



\- PCI device matching

\- PCI config space reads

\- BAR enumeration

\- Read-only logging

\- IORegistry visibility checks



Forbidden:



\- MMIO writes

\- VRAM writes

\- GSP initialization

\- Display engine programming

\- Firmware upload

\- Metal registration

