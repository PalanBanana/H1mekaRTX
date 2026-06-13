# Release Readiness Dashboard Diff Guard

## Purpose

Stage 79 adds a diff guard for the release-readiness dashboard frozen snapshot.

This is generated-dashboard versus frozen-snapshot comparison only.

This is not a driver implementation.

This is not driver installation.

This is not driver activation.

This is not provider transition.

This is not device ownership transition.

This is not hardware-path code.

This is not RTX 5070 Metal runtime implementation.

## Guard Rule

The generated dashboard snapshot must match the frozen snapshot for all contract fields.

Expected release-readiness status:

    MANUAL_REVIEW_ONLY_NO_RUNTIME

Expected badge message:

    manual-review-only

Expected runtime policy:

    NO_RUNTIME

Manual review is runtime permission:

    false

## Runtime Rule

The diff guard must never enable runtime.

Manual review only is not runtime permission.

If the generated dashboard attempts to allow RTX 5070 Metal runtime, the guard must fail.

## Snapshot File

- `release-readiness/release-readiness-dashboard.snapshot.json`

## Metal Goal Tracking

- metal_injection_goal: true
- metal_injection_runtime_allowed_now: false

## Safety Boundary

This stage compares the generated release-readiness dashboard to the frozen snapshot only.

It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.

## Next Stage

Stage 80 should add a release-readiness dashboard CI entrypoint script that runs all release-readiness checks without enabling runtime.

Do not add driver runtime, provider transition, device ownership transition, or hardware-path code yet.
