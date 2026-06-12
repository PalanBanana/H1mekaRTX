# SwiftUI File-picker Static Contract

## Purpose

Stage 59 adds a static contract validator for the SwiftUI local report file picker.

This continues actual host-app source validation.

This validates local JSON file picker source only.

This is not a driver implementation.

This is not driver installation.

This is not driver activation.

This is not provider transition.

This is not device ownership transition.

This is not hardware-path code.

This is not RTX 5070 Metal runtime implementation.

## Decision

Current expected decision:

    PASS_SWIFTUI_FILE_PICKER_STATIC_CONTRACT_READY

## Optional Build Probe

By default, the Swift build probe is skipped.

To try a local Swift build probe:

    H1MEKARTX_RUN_SWIFT_BUILD=1 ./scripts/validate-swiftui-file-picker-static-contract.py --root . --out-dir .

The build probe must remain app-source-only and no-runtime.

## Safety Boundary

This stage performs static source scanning and an optional Swift build probe only.

It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.

## Next Stage

Stage 60 should add a local report import result store for the SwiftUI host app.

Do not add driver runtime, provider transition, device ownership transition, or hardware-path code yet.
