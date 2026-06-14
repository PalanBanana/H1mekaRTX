# Local Metal HUD Dry-Run Launch Command Generator

## Purpose

Phase 61B generates local-only dry-run command templates for future Metal HUD / frame pacing capture.

The target remains RTX 5070 only.

Fallback GPU substitution is not accepted as RTX 5070 proof.

This phase is dry-run command generation only.

This phase does not execute generated commands.

This phase does not enable Metal HUD.

This phase does not run a Metal workload.

This phase does not capture a Metal workload.

This phase does not generate a Metal performance report.

This phase does not claim RTX 5070 acceleration.

This phase does not claim RTX 5070 UI smoothness.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration proof.

## Generated Dry-Run Templates

The generator may emit command templates such as:

- `MTL_HUD_ENABLED=1 <TARGET_APP>`
- `MTL_HUD_ENABLED=1 MTL_HUD_LOG_ENABLED=1 <TARGET_APP>`
- `xcrun xctrace record --template <TEMPLATE> --time-limit <DURATION> --launch <TARGET_APP>`

These are templates only.

The generated templates must use placeholders like `<TARGET_APP>`, `<SCENARIO>`, `<DURATION_SECONDS>`, and `<OUTPUT_DIR>`.

No real local private path should be committed.

No environment variable value should be committed.

## Required Inputs

Committed inputs:

- tools/hackintosh/local-metal-hud-environment-capture-prep.json
- tools/hackintosh/local-metal-hud-capture-manifest.json
- release-readiness/local-metal-hud-environment-prep-summary.json
- release-readiness/local-metal-hud-capture-manifest-summary.json
- release-readiness/scenario-marker-aggregation-summary.json

Local-only inputs:

- host-report-bundle/local-metal-hud-environment-prep/local-metal-hud-environment-prep-report.json
- host-report-bundle/local-metal-hud-capture-manifest/local-metal-hud-capture-manifest.json

## Current Proof State

Current RTX 5070 Metal acceleration is not claimed.

Current RTX 5070 UI smoothness is not claimed.

Current WindowServer attribution to RTX 5070 is not proven.

Current Core Animation attribution to RTX 5070 is not proven.

Current QuartzCore attribution to RTX 5070 is not proven.

Current Metal compositor attribution to RTX 5070 is not proven.

Current Dock/transparency/blur acceleration proof is not proven.

Phase 61C is not allowed now.

provider open remains blocked.

IOServiceOpen remains blocked.

BAR mapping remains blocked.

BAR/MMIO mutation remains blocked.

PCI configuration writes remain blocked.

GPU command submission remains blocked.

Metal proof remains blocked.

Dock/transparency/blur proof remains blocked.

## Safety Boundary

This phase does not run xcodebuild build.

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

This phase does not enable Metal HUD.

This phase does not run a Metal workload.

This phase does not capture a Metal workload.

This phase does not generate a Metal performance report.

This phase does not execute generated dry-run commands.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Next Gate

Phase 61C should add a local Metal HUD hard-opt-in capture wrapper.

Phase 61C must require explicit hard opt-in and must still not claim RTX 5070 acceleration.

## Classification

- CLASSIFICATION_LOCAL_METAL_HUD_DRYRUN_LAUNCH_COMMAND_GENERATOR
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_DRYRUN_COMMAND_TEMPLATE_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
