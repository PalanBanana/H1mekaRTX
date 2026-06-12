# Signed Extension Packaging Plan Resolver Fixture Matrix

## Purpose

Stage 74 adds fixture matrix coverage for the signed-extension packaging plan resolver.

This is packaging-plan resolver fixture validation only.

This is not a driver implementation.

This is not driver installation.

This is not driver activation.

This is not provider transition.

This is not device ownership transition.

This is not hardware-path code.

This is not RTX 5070 Metal runtime implementation.

## Fixtures

The matrix validates three cases:

- sample packaging plan remains NOT_READY
- redacted-ready packaging plan becomes MANUAL_REVIEW_ONLY
- runtime-requested packaging plan is rejected

## Runtime Rule

The resolver matrix must never enable runtime.

Even when redacted-ready packaging evidence is present, runtime remains disabled.

If a packaging plan claims runtime is allowed, the resolver must reject it.

## Expected Decisions

Sample packaging plan:

    NOT_READY_SIGNED_EXTENSION_PACKAGING_EVIDENCE_REQUIRED

Redacted-ready packaging plan:

    PACKAGING_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME

Runtime-requested negative packaging plan:

    NOT_READY_SIGNED_EXTENSION_PACKAGING_EVIDENCE_REQUIRED

## Metal Goal Tracking

- metal_injection_goal: true
- metal_injection_runtime_allowed_now: false

## Safety Boundary

This stage validates signed-extension packaging plan resolver fixture matrix coverage only.

It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.

## Next Stage

Stage 75 should add a combined entitlement-plus-packaging gate summary while keeping runtime disabled.

Do not add driver runtime, provider transition, device ownership transition, or hardware-path code yet.
