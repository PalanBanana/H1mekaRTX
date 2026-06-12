# SwiftUI Store Actions Static Contract

## Purpose

Stage 63 adds a static contract validator for the SwiftUI local store UI actions.

This continues actual host-app source validation.

This validates local UI actions only.

This is not a driver implementation.

This is not driver installation.

This is not driver activation.

This is not provider transition.

This is not device ownership transition.

This is not hardware-path code.

This is not RTX 5070 Metal runtime implementation.

## Decision

Current expected decision:

    PASS_SWIFTUI_STORE_ACTIONS_STATIC_CONTRACT_READY

## Optional Build Probe

By default, the Swift build probe is skipped.

To try a local Swift build probe:

    H1MEKARTX_RUN_SWIFT_BUILD=1 ./scripts/validate-swiftui-store-actions-static-contract.py --root . --out-dir .

The build probe must remain app-source-only and no-runtime.

## Metal Goal Tracking

- metal_injection_goal: true
- metal_injection_runtime_allowed_now: false

## Safety Boundary

This stage performs static source scanning and an optional Swift build probe only.

It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.

## Next Stage

Stage 64 should add a host-app UI navigation/layout consolidation pass.

Do not add driver runtime, provider transition, device ownership transition, or hardware-path code yet.
