# System Settings Approval Runbook

## Purpose

Track the future user approval flow for signed System Extension and DriverKit activation testing.

This stage is documentation-only.

## Future Approval Flow

1. Build signed Host App.
2. Open Host App.
3. Click Request Activation.
4. Wait for macOS approval prompt.
5. Open System Settings.
6. Approve the System Extension if prompted.
7. Reopen Host App.
8. Run diagnostics script.
9. Check systemextensionsctl list.
10. Check sysextd and DriverKit logs.

## Diagnostics

- ./scripts/collect-sysext-diagnostics.sh
- ./scripts/check-signing-readiness.sh
- systemextensionsctl list
- log show --last 30m --style compact --predicate 'process == "sysextd"'

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de

## Boundary

This document does not enable real activation.

No graphics acceleration, MMIO writes, BAR access, GPU reset, GSP initialization, display engine initialization, framebuffer support, or Metal support is attempted.
