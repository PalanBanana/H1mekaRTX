# Release Readiness Workflow Static Contract

## Purpose

Stage 82 adds a workflow static contract for the top-level release-readiness CI wrapper.

This stage also records RTX 5070 Metal full graphics acceleration as a requested goal.

This is workflow validation and intent recording only.

This is not a driver implementation.

This is not driver installation.

This is not driver activation.

This is not provider transition.

This is not device ownership transition.

This is not hardware-path code.

This is not RTX 5070 Metal runtime implementation.

## Runtime Intent

Requested Metal full graphics acceleration:

    true

Desired RTX 5070 Metal runtime state:

    true

Effective RTX 5070 Metal runtime allowed:

    false

## Runtime Rule

Requested true is not the same as allowed true.

The workflow static contract must keep effective runtime disabled.

Manual review only is not runtime permission.

## Expected Decision

Expected checker decision:

    PASS_RELEASE_READINESS_WORKFLOW_STATIC_CONTRACT_READY

## Metal Goal Tracking

- metal_injection_goal: true
- metal_injection_runtime_allowed_now: false
- rtx5070_metal_runtime_allowed: false

## Safety Boundary

This stage validates workflow wiring and runtime intent recording only.

It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.

## Next Stage

Stage 83 should add a runtime milestone map that separates requested RTX 5070 Metal runtime from effective runtime permission.

Do not add driver runtime, provider transition, device ownership transition, or hardware-path code yet.
