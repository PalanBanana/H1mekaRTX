# Signed Build Command Template

## Purpose

Track future signed build commands for Host App and DriverKit activation testing.

This stage is documentation-only.

## Values To Fill Later

- Apple Developer Team ID:
- Host App bundle identifier:
- DriverKit extension bundle identifier:
- Host App provisioning profile:
- DriverKit provisioning profile:

## Future Host App Signed Build

xcodebuild -project apps/H1mekaRTXProbeHost/H1mekaRTXProbeHost.xcodeproj -scheme H1mekaRTXProbeInstaller -configuration Debug DEVELOPMENT_TEAM=TEAM_ID CODE_SIGN_STYLE=Manual build

## Future DriverKit Signed Build

xcodebuild -project apps/H1mekaRTXProbeHost/H1mekaRTXProbeHost.xcodeproj -scheme H1mekaRTXProbeHost -configuration Debug DEVELOPMENT_TEAM=TEAM_ID CODE_SIGN_STYLE=Manual build

## Boundary

This document does not enable real activation.

No graphics acceleration, MMIO writes, BAR access, GPU reset, GSP initialization, display engine initialization, framebuffer support, or Metal support is attempted.
