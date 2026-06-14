# Dock Transparency Blur Scenario Marker

## Purpose

Phase 60W adds a local-only scenario marker for Dock, transparency, blur, window movement, resize, Mission Control, Launchpad, Stage Manager, and desktop space switching.

The target remains RTX 5070 only.

Fallback GPU substitution is not accepted as RTX 5070 proof.

This marker captures scenario timing and local context only.

This marker does not claim RTX 5070 acceleration.

This marker does not claim RTX 5070 UI smoothness.

This marker does not claim Metal proof.

This marker does not claim Dock/transparency/blur acceleration proof.

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

## Supported Scenarios

The marker supports:

- dock_magnification
- dock_hide_show
- dock_launch_animation
- menu_bar_transparency
- window_transparency
- sheet_blur
- sidebar_blur
- window_movement
- window_resize
- mission_control
- launchpad
- stage_manager
- desktop_space_switching

## Manual Workflow

For each scenario:

1. Run marker start.
2. Perform the scenario manually.
3. Run marker end.
4. Keep raw output under host-report-bundle only.
5. Commit only sanitized release-readiness summaries.

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

Phase 60X should add scenario marker aggregation and a baseline timing table.

## Classification

- CLASSIFICATION_DOCK_TRANSPARENCY_BLUR_SCENARIO_MARKER
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_UI_SCENARIO_MARKER_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
