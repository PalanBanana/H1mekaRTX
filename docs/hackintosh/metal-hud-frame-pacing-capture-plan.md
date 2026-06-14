# Metal HUD / Frame Pacing Capture Plan

## Purpose

Phase 60Y defines a Metal HUD and frame pacing capture plan that links local Dock/transparency/blur scenario markers to future graphics timing evidence.

The target remains RTX 5070 only.

Fallback GPU substitution is not accepted as RTX 5070 proof.

This phase is a capture plan only.

This phase does not enable Metal HUD.

This phase does not run a Metal workload.

This phase does not claim RTX 5070 acceleration.

This phase does not claim RTX 5070 UI smoothness.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration proof.

## Inputs

Committed inputs:

- tools/hackintosh/rtx5070-ui-smoothness-evidence-matrix.json
- tools/hackintosh/local-readonly-rtx5070-ui-baseline-collector.json
- tools/hackintosh/dock-transparency-blur-scenario-marker.json
- tools/hackintosh/scenario-marker-aggregation.json
- release-readiness/scenario-marker-aggregation-summary.json

Local-only future inputs:

- Metal HUD logs
- Metal HUD performance reports
- manual Dock/transparency/blur scenario timing markers
- WindowServer/Dock process observations
- display inventory
- RTX 5070 local inventory

## Capture Plan

For each UI scenario:

1. Record scenario marker start.
2. Enable or prepare Metal HUD / frame pacing logging for the target capture context.
3. Perform the manual UI scenario.
4. Record scenario marker end.
5. Store raw HUD/report output under host-report-bundle only.
6. Commit only sanitized rollup fields.

## Required Future Scenario Coverage

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

## Required Future Metrics

- gpu_time_avg
- cpu_time_avg
- frame_time_avg
- frame_time_min
- frame_time_max
- frame_time_p50
- frame_time_p95
- frame_time_p99
- present_delay_avg
- dropped_frame_count
- hitch_count
- encoder_count
- shader_compilation_event_count
- before_after_delta
- scenario_marker_duration_seconds

## Required Attribution Fields

Every future report must separate:

- scenario marker timing
- Metal HUD / frame pacing timing
- WindowServer attribution
- Core Animation attribution
- QuartzCore attribution
- Metal compositor attribution
- RTX 5070 attribution
- fallback GPU attribution

RTX 5070 proof is valid only if RTX 5070 attribution is proven and fallback GPU substitution is false.

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

Phase 60Z should add a local-only Metal HUD capture manifest collector.

The collector must not claim RTX 5070 acceleration.

## Classification

- CLASSIFICATION_METAL_HUD_FRAME_PACING_CAPTURE_PLAN
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_CAPTURE_PLAN_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
