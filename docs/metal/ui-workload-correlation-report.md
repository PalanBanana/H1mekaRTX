# UI Workload Correlation Report

## Purpose

Combine existing host diagnostics, UI compositor sample diagnostics, and UI GPU attribution candidate diagnostics into a report-only correlation candidate.

This is Graphics stack diagnostics.

This is not Runtime probe.

This is not Real GPU command execution.

This is not UI compositor proof.

This is not Metal proof.

## Usage

Generate:

    ./scripts/generate-ui-workload-correlation-report.py \
      --host-summary ./host-diagnostics-summary.json \
      --ui-sample-summary ./ui-compositor-sample-summary.json \
      --ui-gpu-attribution-summary ./ui-gpu-attribution-summary.json \
      --out-dir .

Check with fixtures:

    ./scripts/check-ui-workload-correlation-report.py --root . --out-dir .

## Result Classification

The report may produce:

    UI_WORKLOAD_CORRELATION_CANDIDATES_CAPTURED

That means only that host target visibility, UI sample hints, UI GPU attribution candidate hints, and sample window metadata were present in existing reports.

It does not mean RTX 5070 executed UI compositor work.

It does not mean WindowServer, Core Animation, Dock, Mission Control, Launchpad, transparency, blur, or animation work was GPU-backed by RTX 5070.

## Explicit Non-Claims

- RTX 5070 workload attribution result: `UNPROVEN`.
- Trusted RTX 5070 workload attribution result: `UNPROVEN`.
- Real GPU command execution result: `NOT_ATTEMPTED`.
- UI surface correlation result: `UNPROVEN`.
- UI compositor proof: `UNPROVEN`.
- Metal proof: `UNPROVEN`.
- RTX 5070 UI acceleration claim: `NOT_CLAIMED`.
- RTX 5070 Metal acceleration claim: `NOT_CLAIMED`.

## Safety Boundary

No live diagnostics.

No DriverKit activation.

No System Extension activation.

No device ownership request.

No process injection.

No WindowServer injection.

No Dock injection.

No private framework patching.

No SIP bypass.

No AMFI bypass.

No PCI config-space writes.

No MMIO reads.

No MMIO writes.

No BAR mapping.

No GPU command submission.

No RTX 5070 shader execution.

No RTX 5070 memory movement.

No trusted RTX 5070 workload attribution claim.

No RTX 5070 UI compositor acceleration claim.

No RTX 5070 Metal acceleration claim.
