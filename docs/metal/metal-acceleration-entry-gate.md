# Metal Acceleration Entry Gate

## Purpose

Answer when real RTX 5070 Metal acceleration development can start, using the current Phase 1 and Phase 2 reports.

Metal research development is in progress now.

Runtime probe development is the next phase.

Real RTX 5070 Metal acceleration implementation is blocked until runtime probe, DriverKit/System Extension, read-only BAR probe, real command execution, UI compositor proof, and Metal-facing proof gates are closed.

This is Static contract plus existing-report review.

This is not Runtime probe.

This is not Real GPU command execution.

This is not UI compositor proof.

This is not Metal proof.

## Usage

Generate:

    ./scripts/generate-metal-acceleration-entry-gate.py \
      --host-summary ./host-diagnostics-summary.json \
      --bar-inventory-summary ./bar-inventory-summary.json \
      --ui-compositor-readiness-matrix ./ui-compositor-readiness-matrix.json \
      --ui-workload-correlation-report ./ui-workload-correlation-report.json \
      --out-dir .

Check with fixtures:

    ./scripts/check-metal-acceleration-entry-gate.py --root . --out-dir .

## Plain Answer

- Metal research development: `IN_PROGRESS_NOW`.
- Runtime probe development: `NEXT_PHASE`.
- Real RTX 5070 Metal acceleration implementation: `BLOCKED`.

## Real Metal Acceleration Starts After

- Phase 3 runtime probe evidence
- Phase 4/5 reversible DriverKit/System Extension activation gate
- Phase 6 PCIDriverKit device matching and read-only BAR probe
- Phase 7 real GPU command submission proof
- Phase 8 UI compositor proof
- Phase 9 Metal-facing proof

## Explicit Non-Claims

- No real GPU command execution claim.
- No RTX 5070 UI compositor acceleration claim.
- No RTX 5070 Metal acceleration claim.
- No Metal-facing proof claim.

## Safety Boundary

No live diagnostics.

No DriverKit activation.

No System Extension activation.

No device ownership request.

No process injection.

No WindowServer injection.

No Dock injection.

No private framework patching.

No fake Metal device spoofing.

No SIP bypass.

No AMFI bypass.

No PCI config-space reads.

No PCI config-space writes.

No MMIO reads.

No MMIO writes.

No BAR mapping.

No BAR poking.

No GPU command submission.

No RTX 5070 shader execution.

No RTX 5070 memory movement.

No firmware loading.

No GSP initialization.

No display engine initialization.

No framebuffer initialization.

No GPU reset.

No RTX 5070 UI compositor acceleration claim.

No RTX 5070 Metal acceleration claim.
