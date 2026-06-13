# Release Readiness CI Wrapper

## Purpose

Stage 81 adds a top-level release-readiness CI wrapper.

This is CI wrapper validation only.

This is not a driver implementation.

This is not driver installation.

This is not driver activation.

This is not provider transition.

This is not device ownership transition.

This is not hardware-path code.

This is not RTX 5070 Metal runtime implementation.

## Wrapper

The wrapper script is:

    scripts/run-release-readiness-ci.sh

It runs:

- release-readiness dashboard CI entrypoint
- repository safety gates

## GitHub Actions

The workflow is:

    .github/workflows/release-readiness.yml

Expected wrapper decision:

    PASS_RELEASE_READINESS_CI_WRAPPER

Expected checker decision:

    PASS_RELEASE_READINESS_CI_WRAPPER_READY

## Runtime Rule

The CI wrapper must never enable runtime.

Manual review only is not runtime permission.

If a release-readiness step attempts to allow RTX 5070 Metal runtime, the CI wrapper must fail.

## Metal Goal Tracking

- metal_injection_goal: true
- metal_injection_runtime_allowed_now: false

## Safety Boundary

This stage adds a top-level release-readiness CI wrapper only.

It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.

## Next Stage

Stage 82 should add a GitHub Actions workflow static contract for the top-level release-readiness CI wrapper while keeping runtime disabled.

Do not add driver runtime, provider transition, device ownership transition, or hardware-path code yet.
