# Local Metal HUD Environment Capture Prep

## Purpose

Phase 61A captures local Metal HUD environment readiness.

The target remains RTX 5070 only.

Fallback GPU substitution is not accepted as RTX 5070 proof.

This phase is environment preparation only.

This phase does not enable Metal HUD.

This phase does not run a Metal workload.

This phase does not capture a Metal workload.

This phase does not generate a Metal performance report.

This phase does not claim RTX 5070 acceleration.

This phase does not claim RTX 5070 UI smoothness.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration proof.

## Read-Only Environment Inputs

The local collector may inspect:

- xcodebuild availability
- xcodebuild version
- xcrun availability
- xctrace availability
- metal tool availability
- metallib tool availability
- active developer directory
- selected HUD-related environment variable names only
- scenario marker aggregation summary presence
- local Metal HUD capture manifest summary presence

Environment variable values must not be committed.

Raw command output remains under host-report-bundle only.

## Current Proof State

Current RTX 5070 Metal acceleration is not claimed.

Current RTX 5070 UI smoothness is not claimed.

Current WindowServer attribution to RTX 5070 is not proven.

Current Core Animation attribution to RTX 5070 is not proven.

Current QuartzCore attribution to RTX 5070 is not proven.

Current Metal compositor attribution to RTX 5070 is not proven.

Current Dock/transparency/blur acceleration proof is not proven.

Phase 61B is not allowed now.

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

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Next Gate

Phase 61B should add a local Metal HUD dry-run launch command generator.

Phase 61B must still require hard opt-in and must not claim RTX 5070 acceleration.

## Classification

- CLASSIFICATION_LOCAL_METAL_HUD_ENVIRONMENT_CAPTURE_PREP
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_ENVIRONMENT_PREP_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
