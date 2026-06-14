# RTX 5070 UI Smoothness Evidence Matrix

## Purpose

Phase 60U defines the RTX 5070-only evidence matrix for Dock, transparency, blur, window movement, resize, Mission Control, Launchpad, Stage Manager, WindowServer, Core Animation, QuartzCore, and Metal compositor smoothness.

The target remains RTX 5070 only.

Fallback GPU substitution is not allowed as proof.

AMD, Intel iGPU, Apple Silicon, or any other GPU may only be used as a baseline comparator and never as RTX 5070 proof.

## Current State

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

## RTX 5070 Identity

Required RTX 5070 identity:

- vendor-id: `0x10de`
- device-id: `0x2f04`
- IOPCIMatch: `0x2f0410de`

## Evidence Levels

### Level 0: Target Identity

Required evidence:

- RTX 5070 visible in local inventory
- vendor-id equals `0x10de`
- device-id equals `0x2f04`
- IOPCIMatch equals `0x2f0410de`

### Level 1: Apple Entitlement Readiness

Required evidence:

- paid Apple Developer Program team proven
- System Extension capability proven
- DriverKit entitlement approval proven
- DriverKit PCI transport entitlement approval proven
- host profile proven
- dext profile proven

### Level 2: Real DriverKit Build

Required evidence:

- real_driverkit_dext_built=true
- Xcode-built DriverKit dext binary proven
- selected dext identifier matches `dev.h1meka.H1mekaRTXDriver`
- DriverKit entitlement present
- PCI transport entitlement present
- codesign verification passes

### Level 3: System Extension Visibility

Required evidence:

- activation submitted from `/Applications`
- extension identifier observed by systemextensionsctl
- delegate did not fail
- extension visible after activation

### Level 4: RTX 5070 Provider Readiness

Required evidence:

- provider match visible
- provider belongs to RTX 5070 identity
- provider open not attempted until explicit later gate
- IOServiceOpen not attempted until explicit later gate

### Level 5: GPU Work Authorization

Required evidence:

- future provider-open gate approved
- future BAR mapping gate approved
- future GPU command-submission gate approved
- no BAR/MMIO mutation before explicit approval
- no PCI config writes before explicit approval

### Level 6: Compositor Attribution

Required evidence:

- WindowServer attribution to RTX 5070
- Core Animation attribution to RTX 5070
- QuartzCore attribution to RTX 5070
- Metal compositor attribution to RTX 5070
- no fallback GPU attribution accepted as RTX 5070 proof

### Level 7: Smoothness Measurement

Required scenarios:

- Dock magnification
- Dock hide/show
- Dock launch animation
- menu bar transparency
- window transparency
- sheet blur
- sidebar blur
- window movement
- window resize
- Mission Control
- Launchpad
- Stage Manager
- desktop space switching

Required metrics:

- display refresh rate
- average frame interval
- p50 frame interval
- p95 frame interval
- p99 frame interval
- dropped frame count
- hitch count
- latency average
- latency p95
- jitter score
- before/after delta

### Level 8: RTX 5070 UI Smoothness Proof

Required final proof:

- all previous levels pass
- before/after smoothness delta is positive
- RTX 5070 attribution is proven
- fallback GPU substitution is false
- spoofed Metal support is false
- fake UI acceleration badge is false

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

Phase 60V should add a local read-only RTX 5070 UI smoothness baseline collector.

The collector may gather local-only display/WindowServer/Dock/System Information evidence, but must not claim RTX 5070 acceleration.

## Classification

- CLASSIFICATION_RTX5070_UI_SMOOTHNESS_EVIDENCE_MATRIX
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_UI_SMOOTHNESS_PROOF_LADDER
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
