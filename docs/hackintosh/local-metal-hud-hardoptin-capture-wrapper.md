# Local Metal HUD Hard-Opt-In Capture Wrapper

## Purpose

Phase 61C adds a local-only hard-opt-in wrapper for future Metal HUD / frame pacing capture.

The target remains RTX 5070 only.

Fallback GPU substitution is not accepted as RTX 5070 proof.

This phase adds a wrapper only.

This phase does not execute the wrapper in CI.

This phase does not enable Metal HUD during verification.

This phase does not run a Metal workload during verification.

This phase does not capture a Metal workload during verification.

This phase does not generate a Metal performance report during verification.

This phase does not claim RTX 5070 acceleration.

This phase does not claim RTX 5070 UI smoothness.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration proof.

## Hard Opt-In Rules

The wrapper must refuse unless all required hard opt-in fields are present:

- `--i-understand-local-metal-hud-capture`
- `--execute-capture`
- `--target-app`
- `--scenario`
- `--duration-seconds`
- `--output-under-host-report-bundle`

If any flag is missing, the wrapper must write a refusal report and exit non-zero.

## Future Local Capture Flow

A future local run may:

1. Record scenario marker start.
2. Launch target app with Metal HUD environment variables.
3. Wait for the requested duration.
4. Record scenario marker end.
5. Collect only local logs under host-report-bundle.
6. Summarize sanitized booleans/counts into release-readiness.

## Environment Variables

The wrapper may prepare these environment variables for the child process only:

- `MTL_HUD_ENABLED=1`
- `MTL_HUD_LOG_ENABLED=1`
- `MTL_HUD_LOG_SHADER_ENABLED=1`

Environment values must not be committed to release-readiness.

Raw local logs must stay under host-report-bundle.

## Current Proof State

Current RTX 5070 Metal acceleration is not claimed.

Current RTX 5070 UI smoothness is not claimed.

Current WindowServer attribution to RTX 5070 is not proven.

Current Core Animation attribution to RTX 5070 is not proven.

Current QuartzCore attribution to RTX 5070 is not proven.

Current Metal compositor attribution to RTX 5070 is not proven.

Current Dock/transparency/blur acceleration proof is not proven.

Phase 61D is not allowed now.

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

This phase does not enable Metal HUD during verification.

This phase does not run a Metal workload during verification.

This phase does not capture a Metal workload during verification.

This phase does not generate a Metal performance report during verification.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Next Gate

Phase 61D should add a sanitized local Metal HUD capture summary parser.

Phase 61D must still not claim RTX 5070 acceleration unless RTX 5070 attribution is proven.

## Classification

- CLASSIFICATION_LOCAL_METAL_HUD_HARDOPTIN_CAPTURE_WRAPPER
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_HARDOPTIN_LOCAL_CAPTURE_WRAPPER_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
