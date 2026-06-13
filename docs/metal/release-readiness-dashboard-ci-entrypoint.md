# Release Readiness Dashboard CI Entrypoint

## Purpose

Stage 80 adds a release-readiness dashboard CI entrypoint.

This is CI entrypoint validation only.

This is not a driver implementation.

This is not driver installation.

This is not driver activation.

This is not provider transition.

This is not device ownership transition.

This is not hardware-path code.

This is not RTX 5070 Metal runtime implementation.

## Entrypoint

The entrypoint script is:

    scripts/run-release-readiness-dashboard-ci.sh

It runs:

- release-readiness dashboard diff guard
- release-readiness dashboard static contract check
- release-readiness dashboard check
- combined gate badge check
- combined entitlement packaging gate summary check

## Expected Decision

Expected CI report decision:

    PASS_RELEASE_READINESS_DASHBOARD_CI

Expected checker decision:

    PASS_RELEASE_READINESS_DASHBOARD_CI_ENTRYPOINT_READY

## Runtime Rule

The CI entrypoint must never enable runtime.

Manual review only is not runtime permission.

If a release-readiness check attempts to allow RTX 5070 Metal runtime, the CI entrypoint must fail.

## Metal Goal Tracking

- metal_injection_goal: true
- metal_injection_runtime_allowed_now: false

## Safety Boundary

This stage adds a release-readiness dashboard CI entrypoint only.

It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.

## Next Stage

Stage 81 should add a top-level release-readiness CI wrapper that can be called from GitHub Actions while keeping runtime disabled.

Do not add driver runtime, provider transition, device ownership transition, or hardware-path code yet.
