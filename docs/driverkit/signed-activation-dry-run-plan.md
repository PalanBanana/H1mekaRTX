# Signed Activation Dry Run Plan

## Purpose

Track a future signed activation dry run flow for the Host App and DriverKit extension.

This stage is documentation-only.

## Preconditions

- Apple Developer Team ID is available
- Host App provisioning profile exists
- DriverKit provisioning profile exists
- System Extension install entitlement is approved
- DriverKit entitlement is approved
- PCI transport entitlement is approved
- Signing readiness audit passes

## Dry Run Flow

1. Build signed Host App.
2. Build signed DriverKit extension.
3. Open Host App.
4. Click Request Activation.
5. Approve in System Settings if prompted.
6. Run diagnostics script.
7. Check systemextensionsctl list.
8. Check sysextd and DriverKit logs.

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de

## Boundary

This document does not enable real activation.

No graphics acceleration, MMIO writes, BAR access, GPU reset, GSP initialization, display engine initialization, framebuffer support, or Metal support is attempted.
