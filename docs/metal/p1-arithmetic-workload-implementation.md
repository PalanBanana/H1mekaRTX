# P1 Arithmetic Workload Implementation

## Purpose

Stage 35 implements the P1 arithmetic workload expansion for the public Metal reference workload suite.

This is safe app-level Metal production.

This is not RTX 5070 Metal acceleration implementation.

## Decision

Current decision:

    PASS_P1_ARITHMETIC_WORKLOADS_READY

## Goal

The long-term goal remains full Metal graphics acceleration research for RTX 5070 on macOS.

This stage grows the deterministic public Metal workload suite on the existing system Metal device only.

## Existing Workloads

- vector_add
- saxpy
- square

## New P1 Workloads

- vector_multiply
- vector_subtract
- axpby

## Runtime Behavior

The harness:

- obtains the default system Metal device
- creates a command queue
- compiles reference Metal shader source at runtime
- creates compute pipelines
- creates shared buffers
- dispatches compute workloads
- validates deterministic CPU-expected outputs
- prints JSON runtime results

## Run

From the repository root:

    cd tools/metal-validation-harness
    swift run

## Static Check

From the repository root:

    ./scripts/check-p1-arithmetic-workload-implementation.py --root . --out-dir .

Optional build check on macOS:

    ./scripts/check-p1-arithmetic-workload-implementation.py --root . --out-dir . --build

Optional runtime check on macOS:

    ./scripts/check-p1-arithmetic-workload-implementation.py --root . --out-dir . --build --run

## Safety Boundary

This stage is limited to the existing system Metal device.

It does not perform:

- RTX 5070 Metal acceleration attempts
- RTX 5070 shader execution
- hardware command submission to RTX 5070
- RTX 5070 resource allocation
- ioreg collection
- system_profiler collection
- PCI config-space reads
- PCI config-space writes
- MMIO reads
- MMIO writes
- BAR memory mapping
- BAR memory poking
- DriverKit activation
- System Extension activation
- device ownership request
- firmware loading
- GSP initialization
- display engine initialization
- framebuffer initialization
- GPU reset logic

## Next Stage

Stage 36 should update the workload result schema and regression manifest to include the new P1 workloads.
