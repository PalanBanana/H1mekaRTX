# Host App No-activation Skeleton

## Purpose

Stage 27 adds a no-activation host app skeleton for the DriverKit/System Extension research track.

This is a Swift package skeleton.

This is not a DriverKit activation stage.

This does not add a DriverKit dext target.

This does not add System Extension request code.

## Decision

Current decision:

    PASS_HOST_APP_SKELETON_NO_ACTIVATION

## Goal

The long-term goal remains full Metal graphics acceleration research for RTX 5070 on macOS.

This stage creates a safe host-side skeleton that reports planned state and safety boundaries.

## Current Behavior

The skeleton prints a JSON report containing:

- target PCI identity
- host skeleton presence
- planned panels
- activation disabled state
- deactivation disabled state
- manager submit disabled state
- device ownership disabled state
- RTX 5070 acceleration disabled state
- BAR/MMIO disabled state

## Run

From the repository root:

    cd tools/host-app-no-activation
    swift run

## Static Check

From the repository root:

    ./scripts/check-host-app-no-activation-skeleton.py --root . --out-dir .

Optional build check on macOS:

    ./scripts/check-host-app-no-activation-skeleton.py --root . --out-dir . --build

## Safety Boundary

This stage does not perform:

- DriverKit dext target creation
- System Extension activation request creation
- System Extension deactivation request creation
- manager submit calls
- DriverKit activation
- IOPCIDevice ownership request
- ioreg collection
- system_profiler collection
- PCI config-space reads
- PCI config-space writes
- MMIO reads
- MMIO writes
- BAR memory mapping
- BAR memory poking
- RTX 5070 shader execution
- hardware command submission
- RTX 5070 resource allocation
- firmware loading
- GSP initialization
- display engine initialization
- framebuffer initialization
- GPU reset logic
- RTX 5070 Metal acceleration implementation

## Next Stage

Stage 28 should add a no-activation host status schema or continue host-side UI planning without System Extension requests.
