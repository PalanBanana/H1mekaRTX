# Entitlement Evidence Resolver

## Purpose

Stage 68 adds a redacted entitlement evidence resolver.

This resolver reads a redacted evidence file and emits GO or NO-GO for manual review.

This is an evidence resolver only.

This is not a driver implementation.

This is not driver installation.

This is not driver activation.

This is not provider transition.

This is not device ownership transition.

This is not hardware-path code.

This is not RTX 5070 Metal runtime implementation.

## Default Decision

With the default sample evidence file, the expected decision is:

    NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE

## Runtime Rule

Even if all evidence fields are later filled with redacted provided values, this resolver still does not enable runtime.

The resolver may only mark evidence as present for manual review.

Runtime remains controlled by later separate gates.

## Metal Goal Tracking

- metal_injection_goal: true
- metal_injection_runtime_allowed_now: false

## Safety Boundary

This stage resolves redacted entitlement evidence only.

It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.

## Next Stage

Stage 69 should add a resolver static contract checker and a redacted-ready fixture that still keeps runtime disabled.

Do not add driver runtime, provider transition, device ownership transition, or hardware-path code yet.
