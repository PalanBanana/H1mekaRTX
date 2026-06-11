# Local Signing Config Map

## Purpose

Track local Xcode signing values needed before a future signed System Extension and DriverKit activation attempt.

This stage is documentation-only.

## Values To Fill Later

- Apple Developer Team ID:
- Host App bundle identifier:
- DriverKit extension bundle identifier:
- Host App provisioning profile name:
- DriverKit provisioning profile name:
- Signing certificate name:

## Host App Signing

- CODE_SIGN_STYLE should be Manual or Automatic after profiles exist.
- DEVELOPMENT_TEAM must match the Apple Developer Team ID.
- CODE_SIGN_ENTITLEMENTS must point to the Host App entitlements file.
- PRODUCT_BUNDLE_IDENTIFIER must match the Host App App ID.

## Host App Signing

- CODE_SIGN_STYLE should be Manual or Automatic after profiles exist.
- DEVELOPMENT_TEAM must match the Apple Developer Team ID.
- CODE_SIGN_ENTITLEMENTS must point to the Host App entitlements file.
- PRODUCT_BUNDLE_IDENTIFIER must match the Host App App ID.

## DriverKit Signing

- DEVELOPMENT_TEAM must match the Apple Developer Team ID.
- PRODUCT_BUNDLE_IDENTIFIER must match the DriverKit extension App ID.
- Provisioning profile must include DriverKit entitlement.
- Provisioning profile must include PCI transport entitlement.

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de

## Boundary

This document does not enable real activation.

No graphics acceleration, MMIO writes, BAR access, GPU reset, GSP initialization, display engine initialization, framebuffer support, or Metal support is attempted.
