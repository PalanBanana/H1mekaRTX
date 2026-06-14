# RTX 5070 Accelerated Bring-Up Critical Path Gate

## Purpose

Phase 62A compresses the RTX 5070 acceleration bring-up path into one critical-path gate.

This is the fastest safe route toward real Dock/transparency/blur acceleration.

The target remains RTX 5070 only.

Fallback GPU substitution is not accepted as RTX 5070 proof.

This phase does not perform hardware mutation.

This phase does not submit GPU commands.

This phase does not claim acceleration.

## Required Critical Path

Real Dock/transparency/blur acceleration requires all of these gates:

1. DriverKit entitlement gate
2. PCIDriverKit transport entitlement gate
3. System Extension provisioning gate
4. Provider match gate
5. Provider open policy gate
6. Safe BAR access design gate
7. BAR read-only proof gate
8. BAR mutation approval gate
9. Minimal GPU command path design gate
10. Minimal GPU command path hard-opt-in gate
11. GPU command completion evidence gate
12. Framebuffer/display path design gate
13. Framebuffer/display path hard-opt-in gate
14. WindowServer attribution gate
15. Core Animation attribution gate
16. QuartzCore attribution gate
17. Metal compositor attribution gate
18. Dock/transparency/blur scenario metric gate
19. RTX 5070-only attribution proof gate

## Current Fastest Reality

Current RTX 5070 identity evidence exists locally, but RTX 5070 Metal acceleration is not proven.

Current UI marker and Metal HUD infrastructure exists, but RTX 5070 Dock/transparency/blur acceleration is not proven.

DriverKit/PCIDriverKit entitlement approval is the largest external blocker.

Provider match and provider open cannot be treated as proven until entitlement/provisioning is valid.

Safe BAR design must remain default-deny until entitlement/provider state is proven.

Minimal GPU command path must remain blocked until safe BAR and provider gates pass.

Framebuffer/display path must remain blocked until minimal GPU command completion evidence exists.

Metal compositor attribution must remain blocked until WindowServer/Core Animation/QuartzCore attribution is captured without fallback GPU substitution.

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

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Next Gate

Phase 62B should add Apple Developer / DriverKit / PCIDriverKit entitlement request package automation.

## Classification

- CLASSIFICATION_RTX5070_ACCELERATED_BRINGUP_CRITICAL_PATH_GATE
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_ACCELERATION_GATE_NOT_ACCELERATION
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
