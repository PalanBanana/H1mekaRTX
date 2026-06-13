# UI Compositor Readiness Matrix

## Purpose

Combine existing host diagnostics, UI compositor sample diagnostics, optional UI GPU attribution candidate diagnostics, optional UI workload correlation candidate diagnostics, and the UI compositor proof schema into a readiness matrix.

This matrix shows which prerequisites are present and which proof requirements remain blocked.

This is not Runtime probe.

This is not Real GPU command execution.

This is not UI compositor proof.

This is not Metal proof.

## Inputs

- host-diagnostics-summary.json
- ui-compositor-sample-summary.json
- ui-gpu-attribution-summary.json
- ui-workload-correlation-report.json
- ui-compositor-proof-schema.json

## Output

- ui-compositor-readiness-matrix.json
- ui-compositor-readiness-matrix.md

## Current Expected Decision

    NOT_PROVEN

The expected result is `NOT_PROVEN` until the project has:

- current UI GPU attribution
- RTX 5070 workload attribution during the same sample window
- UI action interval, compositor timing, and RTX 5070-backed work correlation

## Usage

    ./scripts/generate-ui-compositor-readiness-matrix.py \
      --host-summary ./host-diagnostics-summary.json \
      --ui-sample-summary ./ui-compositor-sample-summary.json \
      --ui-gpu-attribution-summary ./ui-gpu-attribution-summary.json \
      --ui-workload-correlation-report ./ui-workload-correlation-report.json \
      --proof-schema ./ui-compositor-proof-schema.json \
      --out-dir .

Check with fixtures:

    ./scripts/check-ui-compositor-readiness-matrix.py --root . --out-dir .

## Explicit Non-Claims

- No RTX 5070 UI compositor acceleration claim.
- No RTX 5070 Metal acceleration claim.
- No GPU command execution claim.
- No Metal proof claim.

## Safety Boundary

This matrix reads existing JSON reports only.

No live diagnostics.

No DriverKit activation.

No System Extension activation.

No device ownership request.

No PCI config-space writes.

No MMIO reads.

No MMIO writes.

No BAR mapping.

No GPU command submission.

No RTX 5070 shader execution.

No WindowServer injection.

No Dock injection.

No private framework patching.

No SIP bypass.

No AMFI bypass.

No fake Metal device spoofing.

No RTX 5070 UI compositor acceleration claim.

No RTX 5070 Metal acceleration claim.
