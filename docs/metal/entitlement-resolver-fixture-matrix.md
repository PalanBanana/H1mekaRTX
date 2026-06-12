# Entitlement Resolver Fixture Matrix

## Purpose

Stage 70 adds CI-style fixture matrix coverage for the entitlement evidence resolver.

This is fixture-matrix validation only.

This is not a driver implementation.

This is not driver installation.

This is not driver activation.

This is not provider transition.

This is not device ownership transition.

This is not hardware-path code.

This is not RTX 5070 Metal runtime implementation.

## Fixtures

The matrix validates three cases:

- sample incomplete evidence stays NO-GO
- redacted-ready evidence becomes manual-review-only GO
- runtime-requested evidence is rejected

## Runtime Rule

The resolver matrix must never enable runtime.

Even when redacted-ready evidence is present, runtime remains disabled.

If an evidence file claims runtime is allowed, the resolver must reject it.

## Expected Decisions

Sample incomplete fixture:

    NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE

Redacted-ready fixture:

    EVIDENCE_PRESENT_RUNTIME_STILL_DISABLED

Runtime-requested negative fixture:

    NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE

## Metal Goal Tracking

- metal_injection_goal: true
- metal_injection_runtime_allowed_now: false

## Safety Boundary

This stage validates resolver fixture matrix coverage only.

It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.

## Next Stage

Stage 71 should begin a signed-extension packaging plan matrix while keeping runtime disabled.

Do not add driver runtime, provider transition, device ownership transition, or hardware-path code yet.
