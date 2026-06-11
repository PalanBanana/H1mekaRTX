# SystemExtensions Activation Status Matrix

## Purpose

Track expected SystemExtensions activation states, user approval states, and failure categories for future signed DriverKit activation testing.

This stage is documentation-only.

## Expected Request States

- Request submitted
- User approval required
- Request finished
- Request failed
- Replacement requested

## Expected Failure Categories

- Missing System Extension install entitlement
- Missing DriverKit entitlement
- Missing PCI transport entitlement
- Invalid provisioning profile
- Bundle identifier mismatch
- Extension not embedded in Host App bundle
- User approval denied or pending
- sysextd validation failure

## Diagnostics To Check

- Host App status text
- systemextensionsctl list
- sysextd logs
- DriverKit logs
- H1mekaRTXProbe logs
- Signing readiness audit output

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de

## Boundary

This document does not enable real activation.

No graphics acceleration, MMIO writes, BAR access, GPU reset, GSP initialization, display engine initialization, framebuffer support, or Metal support is attempted.
