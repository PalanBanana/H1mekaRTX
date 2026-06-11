# Apple Developer Portal Checklist

## Purpose

Track Apple Developer Portal steps needed before real signed System Extension and DriverKit activation testing.

This stage is documentation-only.

## Official Apple Pages

- https://developer.apple.com/system-extensions/
- https://developer.apple.com/documentation/driverkit/requesting-entitlements-for-driverkit-development
- https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.system-extension.install
- https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.driverkit
- https://developer.apple.com/help/account/provisioning-profiles/create-a-driverkit-development-provisioning-profile/

## Required Account Info

- Apple Developer Team ID:
- Account Holder Apple ID:
- Host App bundle identifier:
- DriverKit extension bundle identifier:
- Activation request identifier:
- Repository URL: https://github.com/PalanBanana/H1mekaRTX

## Entitlements To Request

Host App:

- com.apple.developer.system-extension.install

DriverKit extension:

- com.apple.developer.driverkit
- com.apple.developer.driverkit.transport.pci

## Portal Checklist

1. Confirm Apple Developer Program membership.
2. Confirm Account Holder access.
3. Open Apple System Extensions and DriverKit request page.
4. Submit entitlement request using the H1mekaRTX entitlement request packet.
5. Wait for Apple review.
6. After approval, create explicit App ID for Host App.
7. Enable System Extension capability for Host App App ID.
8. Create explicit App ID for DriverKit extension.
9. Enable DriverKit capability for DriverKit extension App ID.
10. Create Host App development provisioning profile.
11. Create DriverKit development provisioning profile.
12. Download provisioning profiles.
13. Configure Xcode signing settings.
14. Re-run signing readiness audit.
15. Attempt signed activation only after all signing checks pass.

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de
- Subsystem Vendor ID: 0x1458
- Subsystem ID: 0x417e

## Boundary

This document does not request entitlements automatically.

This document does not enable real DriverKit activation.

## Not In Scope

- Real DriverKit activation
- Metal acceleration
- framebuffer support
- GSP initialization
- display engine initialization
- MMIO writes
- BAR memory poking
- GPU reset logic
