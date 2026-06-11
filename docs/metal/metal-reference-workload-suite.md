# Metal Reference Workload Suite

## Purpose

Stage 25 expands the public Metal app-layer validation harness into a small reference workload suite.

This is real Metal app-layer development.

This is not RTX 5070 Metal acceleration.

## Decision

Current decision:

    PASS_METAL_REFERENCE_WORKLOAD_SUITE_READY

## Goal

The long-term goal remains full Metal graphics acceleration research for RTX 5070 on macOS.

This stage improves the reference workloads that can later be used to compare correctness and reporting behavior.

## Workloads

The suite currently includes:

- `vector_add`
- `saxpy`
- `square`

All workloads use the existing system Metal device only.

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

    ./scripts/check-metal-reference-workload-suite.py --root . --out-dir .

Optional build check on macOS:

    ./scripts/check-metal-reference-workload-suite.py --root . --out-dir . --build

## Safety Boundary

This suite is limited to the existing system Metal device.

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
- IOPCIDevice ownership request
- firmware loading
- GSP initialization
- display engine initialization
- framebuffer initialization
- GPU reset logic

## Notes

This stage proves the project can grow a deterministic public Metal workload suite.

It does not expose the RTX 5070 as a macOS Metal device.

It does not claim RTX 5070 graphics acceleration.
