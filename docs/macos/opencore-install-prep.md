\# OpenCore Install Preparation for H1mekaRTXProbe



This document tracks the OpenCore/Hackintosh preparation plan for testing H1mekaRTXProbe.



\## Purpose



This Hackintosh installation is not intended for daily macOS usage.



Its Stage 1 purpose is only:



\- boot macOS far enough to run terminal commands

\- inspect IORegistry

\- activate a DriverKit dext

\- match the RTX 5070 PCI device

\- collect logs from H1mekaRTXProbe



\## Target Hardware



\- CPU: Intel Core i7-14700K

\- Motherboard: ASRock B760M-PRO-A

\- GPU: NVIDIA GeForce RTX 5070

\- iGPU: Intel UHD Graphics 770

\- Memory: 32 GB

\- Storage: MSI NVMe M450 1 TB



\## Known Display Limitation



The system does not currently have a macOS-supported GPU for graphics acceleration.



Known limitations:



\- RTX 5070 is not expected to provide native macOS graphics acceleration.

\- Intel UHD Graphics 770 is not expected to provide native macOS graphics acceleration.

\- Stage 1 does not depend on graphics acceleration.

\- Stage 1 only requires enough display or remote access to run logs and IORegistry checks.



\## Recommended Installation Strategy



Use a separate test SSD or a fully backed-up partition.



Do not install directly over the main Windows system.



Recommended order:



1\. Prepare a dedicated macOS test disk or partition.

2\. Build a minimal OpenCore EFI.

3\. Boot macOS installer.

4\. Confirm basic terminal access.

5\. Confirm PCI visibility for `10de:2f04`.

6\. Install or activate H1mekaRTXProbe only after the system boots reliably.



\## BIOS Direction



Initial BIOS direction:



\- CSM: Disabled

\- Secure Boot: Disabled

\- Fast Boot: Disabled

\- SATA Mode: AHCI

\- Above 4G Decoding: Enabled

\- Resizable BAR: Test both Enabled and Disabled if boot issues occur

\- VT-d: Enabled, with OpenCore configuration handling as needed

\- Primary Display: PEG / PCIe



\## OpenCore Scope



The EFI should be minimal.



Stage 1 EFI goal:



\- boot macOS

\- avoid unsupported GPU assumptions

\- expose PCI devices

\- keep the system stable enough for DriverKit testing



\## Stage 1 Forbidden Operations



H1mekaRTXProbe must not perform:



\- MMIO writes

\- VRAM writes

\- GSP initialization

\- firmware upload

\- display engine programming

\- Metal registration



\## Success Criteria



The OpenCore test environment is considered usable when:



\- macOS boots to desktop or recovery/terminal

\- IORegistry can be inspected

\- RTX 5070 appears as PCI device `10de:2f04`

\- DriverKit logs can be collected

\- H1mekaRTXProbe can be tested safely

