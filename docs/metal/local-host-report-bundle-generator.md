# Local Host Report Bundle Generator

## Purpose

Stage 38 adds a local-only host report bundle generator.

This is host-side tooling production.

This is not host GUI implementation.

This is not System Extension activation.

This is not DriverKit activation.

This is not RTX 5070 Metal acceleration implementation.

## Decision

Current decision:

    PASS_LOCAL_HOST_REPORT_BUNDLE_GENERATOR_READY

## Bundle Type

    LOCAL_ONLY_REPORT_BUNDLE

## Generator

Script:

    scripts/create-local-host-report-bundle.py

The generator reads already-existing local reports from an input directory and creates:

- host-report-bundle/bundle.json
- host-report-bundle/README.md
- host-report-bundle/reports/*

## Usage

From the repository root:

    ./scripts/create-local-host-report-bundle.py --input-dir . --bundle-dir host-report-bundle

Check with local fixtures:

    ./scripts/check-local-host-report-bundle-generator.py --root . --out-dir .

## Copied Optional Reports

The generator copies these files only if they already exist:

- metal-workload-runtime.json
- metal-workload-result-schema.json
- metal-workload-regression-manifest.json
- host-status.json
- host-diagnostics-summary.json
- host-diagnostics-summary.md
- bar-inventory-summary.json
- bar-inventory-summary.md
- ui-compositor-proof-schema.json
- ui-compositor-proof-schema.md
- ui-compositor-sample-summary.json
- ui-compositor-sample-summary.md
- ui-compositor-readiness-matrix.json
- ui-compositor-readiness-matrix.md
- ui-gpu-attribution-summary.json
- ui-gpu-attribution-summary.md
- ui-workload-correlation-report.json
- ui-workload-correlation-report.md
- metal-acceleration-entry-gate.json
- metal-acceleration-entry-gate.md
- rendered-host-status-report.md
- forbidden-bar-operation-audit.md

## Safety Boundary

This stage is local-file-only.

It only copies existing local reports and writes local bundle metadata.

It does not query live extension state, submit System Extension requests, activate DriverKit, request device ownership, collect live PCI inventory, access PCI configuration space, access MMIO, map BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, load firmware, initialize display paths, initialize framebuffer, or reset the GPU.

## Next Stage

Stage 39 should add a local diagnostics index that references generated reports and bundles without live queries or hardware access.
