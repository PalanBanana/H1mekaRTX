\# DriverKit Entitlement Request Notes



This document tracks the entitlement requirements for H1mekaRTXProbe.



\## Required Entitlements



\- `com.apple.developer.driverkit`

\- `com.apple.developer.driverkit.transport.pci`



\## Target PCI Device



\- Vendor ID: `0x10de`

\- Device ID: `0x2f04`

\- Subsystem Vendor ID: `0x1458`

\- Subsystem Device ID: `0x417e`

\- Revision ID: `0xa1`

\- Class Code: `0x030000`



\## Purpose



H1mekaRTXProbe is a read-only PCI detection driver for NVIDIA RTX 5070.



The first target is not graphics acceleration.



The first target is:



\- match the RTX 5070 PCI device

\- read PCI config space

\- enumerate BARs

\- log PCI IDs and BAR layout

\- appear in IORegistry



\## Safety Policy



The driver must not perform:



\- MMIO writes

\- VRAM writes

\- GSP initialization

\- firmware upload

\- display engine programming

\- Metal registration

