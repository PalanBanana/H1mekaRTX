# Real DriverKit Dext Build Gate

## Purpose

Phase 60L adds a hard opt-in local build gate for a real Xcode-built DriverKit dext.

Phase 60K showed that the current dext is only a generic Mach-O stub and is not proven to be an Xcode-built DriverKit dext binary.

This phase does not create a provider-open path.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not mutate BAR/MMIO.

This phase does not write PCI configuration space.

This phase does not load firmware.

This phase does not reset the GPU.

This phase does not initialize framebuffer or display-engine paths.

This phase does not submit GPU commands.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Why This Gate Exists

The current validationFailed root-cause summary reported:

- spctl rejected host or dext
- developer mode not confirmed on
- real Xcode-built DriverKit dext binary not proven
- DriverKit entitlements present but OS acceptance not proven
- Apple Development signed non-notarized local build

A generic C stub inside a .dext bundle is not enough. The next validation step requires an actual DriverKit target built by Xcode/DriverKit SDK.

## Required Runtime Flags

Actual local Xcode build is allowed only when all flags are present:

- --i-understand-local-driverkit-build
- --output-under-host-report-bundle
- --scheme <XCODE_SCHEME>
- one of:
  - --project <PATH_TO_XCODEPROJ>
  - --workspace <PATH_TO_XCWORKSPACE>

Optional:

- --configuration Debug
- --derived-data-path <PATH>
- --expected-dext-id dev.h1meka.H1mekaRTXDriver

## What The Script May Do With Opt-In

- check xcodebuild availability
- check DriverKit SDK availability
- run xcodebuild build for the provided project/workspace and scheme
- search DerivedData products for a .dext bundle
- verify the .dext executable exists
- inspect file type
- run codesign verify/display
- write local-only raw build report under host-report-bundle
- write sanitized release-readiness summary

## What This Script Must Not Do

- no activation submit
- no deactivation submit
- no install
- no manual dext load
- no provider open
- no IOServiceOpen
- no BAR mapping
- no BAR/MMIO mutation
- no PCI config writes
- no firmware load
- no GPU reset
- no framebuffer/display-engine init
- no GPU command submission
- no Metal proof
- no Dock/transparency/blur proof

## Next Gate

If a real Xcode-built DriverKit dext is proven, rerun:

1. local signing/preflight
2. Phase 60I /Applications activation remediation
3. Phase 60K validationFailed root-cause gate

If validation passes and extension becomes visible, rerun:

1. Phase 58
2. Phase 59
3. Phase 60A
4. Phase 60B

Only then Phase 61 can be considered.

## Classification

- CLASSIFICATION_REAL_DRIVERKIT_DEXT_BUILD_GATE
- CLASSIFICATION_VALIDATIONFAILED_ROOT_CAUSE_GATE
- CLASSIFICATION_LOCAL_BUILD_GATE_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
