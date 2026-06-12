# SwiftUI Layout Static Contract

## Purpose

Stage 65 adds a static contract validator for the SwiftUI host-app layout consolidation.

This continues actual host-app source validation.

This validates navigation, scroll layout, shared import store usage, Metal goal banner, and runtime boundary summary.

This is not a driver implementation.

This is not driver installation.

This is not driver activation.

This is not provider transition.

This is not device ownership transition.

This is not hardware-path code.

This is not RTX 5070 Metal runtime implementation.

## Decision

Current expected decision:

    PASS_SWIFTUI_LAYOUT_STATIC_CONTRACT_READY

## Optional Build Probe

By default, the Swift build probe is skipped.

To try a local Swift build probe:

    H1MEKARTX_RUN_SWIFT_BUILD=1 ./scripts/validate-swiftui-layout-static-contract.py --root . --out-dir .

The build probe must remain app-source-only and no-runtime.

## Metal Goal Tracking

- metal_injection_goal: true
- metal_injection_runtime_allowed_now: false

## Safety Boundary

This stage performs static source scanning and an optional Swift build probe only.

It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.

## Next Stage

Stage 66 should begin the entitlement and provisioning evidence matrix.

Do not add driver runtime, provider transition, device ownership transition, or hardware-path code yet.
