# SystemExtensions Diagnostics

## Purpose

Collect local diagnostics for future signed DriverKit/System Extension activation attempts.

This stage does not attempt real activation.

## Script

Run:

    ./scripts/collect-sysext-diagnostics.sh

Optional output directory:

    ./scripts/collect-sysext-diagnostics.sh ~/Desktop/H1mekaRTX-sysext-diagnostics-test

## Captured Data

- macOS version
- kernel version
- Xcode version
- systemextensionsctl list
- PCI device report
- IORegistry snapshots
- recent sysextd, DriverKit, SystemExtension, and H1mekaRTX related logs

## Boundary

This script is diagnostic-only.

It does not load a driver, activate a system extension, write MMIO, access BAR memory, reset the GPU, initialize display engines, initialize GSP, or attempt graphics acceleration.
