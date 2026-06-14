# Local Read-Only RTX 5070 UI Baseline Collector

## Purpose

Phase 60V adds a local read-only baseline collector for RTX 5070 UI smoothness evidence.

The target remains RTX 5070 only.

Dock smoothness remains in scope.

Transparency / blur smoothness remains in scope.

Window movement and resize smoothness remain in scope.

Mission Control, Launchpad, Stage Manager, WindowServer, Core Animation, QuartzCore, and Metal compositor attribution remain in scope.

Fallback GPU substitution is not accepted as RTX 5070 proof.

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

## Read-Only Inputs

The collector may run these read-only commands:

- system_profiler SPDisplaysDataType -json
- system_profiler SPHardwareDataType -json
- ioreg -r -c IOPCIDevice -l -w0
- ioreg -r -c IOAccelerator -l -w0
- ioreg -r -c IODisplayConnect -l -w0
- ps ax -o pid,comm
- log show --last 5m for WindowServer and Dock
- defaults read com.apple.universalaccess reduceTransparency

Raw output is local-only under host-report-bundle.

Committed release-readiness output must contain only sanitized booleans and counts.

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

## Expected Baseline Result

A valid baseline can say:

- RTX 5070 target identity tokens were observed or not observed.
- WindowServer process was observed or not observed.
- Dock process was observed or not observed.
- Display inventory was collected or not collected.
- Metal support string was observed or not observed in display inventory.
- Reduce Transparency setting was observed or not observed.
- Raw local logs were collected locally only.

A valid baseline cannot say:

- RTX 5070 accelerated Dock.
- RTX 5070 accelerated transparency.
- RTX 5070 accelerated blur.
- RTX 5070 accelerated WindowServer.
- RTX 5070 is a Metal compositor GPU.
- RTX 5070 GPU commands were submitted.

## Next Gate

Phase 60W should add a Dock/transparency/blur scenario runner that records manual scenario timing markers without claiming RTX 5070 acceleration.

## Classification

- CLASSIFICATION_LOCAL_READONLY_RTX5070_UI_BASELINE
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_UI_BASELINE_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
