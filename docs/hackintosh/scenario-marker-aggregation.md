# Scenario Marker Aggregation

## Purpose

Phase 60X aggregates local-only Dock/transparency/blur scenario marker events into a sanitized release-readiness summary.

The target remains RTX 5070 only.

Fallback GPU substitution is not accepted as RTX 5070 proof.

This phase aggregates timing markers only.

This phase does not claim RTX 5070 acceleration.

This phase does not claim RTX 5070 UI smoothness.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration proof.

## Input

Local-only input:

- host-report-bundle/dock-transparency-blur-scenario-marker/scenario-events.json
- host-report-bundle/dock-transparency-blur-scenario-marker/dock-transparency-blur-scenario-marker-report.json

Committed input:

- tools/hackintosh/dock-transparency-blur-scenario-marker.json
- tools/hackintosh/local-readonly-rtx5070-ui-baseline-collector.json
- tools/hackintosh/rtx5070-ui-smoothness-evidence-matrix.json

## Aggregated Fields

The aggregator records:

- scenario count
- event count
- completed session count
- per-scenario start/end counts
- per-scenario completed session counts
- per-scenario min/max/avg duration seconds
- whether WindowServer was observed during markers
- whether Dock was observed during markers
- whether Reduce Transparency state was captured
- whether RTX 5070 acceleration claim remains false
- whether RTX 5070 UI smoothness claim remains false

## Current Proof State

Current RTX 5070 Metal acceleration is not claimed.

Current RTX 5070 UI smoothness is not claimed.

Current WindowServer attribution to RTX 5070 is not proven.

Current Core Animation attribution to RTX 5070 is not proven.

Current QuartzCore attribution to RTX 5070 is not proven.

Current Metal compositor attribution to RTX 5070 is not proven.

Current Dock/transparency/blur acceleration proof is not proven.

Phase 61 is not allowed now.

provider open remains blocked.

IOServiceOpen remains blocked.

BAR mapping remains blocked.

BAR/MMIO mutation remains blocked.

PCI configuration writes remain blocked.

GPU command submission remains blocked.

Metal proof remains blocked.

Dock/transparency/blur proof remains blocked.

## Safety Boundary

This phase does not run xcodebuild.

This phase does not submit activation.

This phase does not submit deactivation.

This phase does not install anything.

This phase does not manually load a dext.

This phase does not open a provider.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not mutate BAR/MMIO.

This phase does not write PCI configuration space.

This phase does not load firmware.

This phase does not reset the GPU.

This phase does not initialize framebuffer or display-engine paths.

This phase does not submit GPU commands.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Next Gate

Phase 60Y should add a Metal Performance HUD / frame pacing capture plan that links these scenario markers to future timing metrics without claiming RTX 5070 acceleration.

## Classification

- CLASSIFICATION_SCENARIO_MARKER_AGGREGATION
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_UI_TIMING_MARKER_AGGREGATION_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
