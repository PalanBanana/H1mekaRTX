# Signed Extension Packaging Plan Matrix

## Purpose

Stage 71 adds a signed-extension packaging plan matrix.

This is packaging planning only.

This is not a driver implementation.

This is not driver installation.

This is not driver activation.

This is not provider transition.

This is not device ownership transition.

This is not hardware-path code.

This is not RTX 5070 Metal runtime implementation.

## Decision

Current expected decision:

    NOT_READY_SIGNED_EXTENSION_PACKAGING_EVIDENCE_REQUIRED

## Packaging Plan Items

The matrix tracks:

- Host app Bundle ID status
- Driver extension Bundle ID status
- Bundle ID pairing status
- DriverKit entitlement status
- DriverKit development profile status
- Extension install permission status
- Developer certificate status
- Distribution signing status
- Notarization status
- Manual review status

## Runtime Rule

The packaging plan must never enable runtime.

The packaging plan only states what evidence must exist before runtime can be discussed in later gates.

## Metal Goal Tracking

- metal_injection_goal: true
- metal_injection_runtime_allowed_now: false

## Safety Boundary

This stage adds a signed-extension packaging plan matrix only.

It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.

## Next Stage

Stage 72 should add a static contract checker for the signed-extension packaging plan matrix.

Do not add driver runtime, provider transition, device ownership transition, or hardware-path code yet.
