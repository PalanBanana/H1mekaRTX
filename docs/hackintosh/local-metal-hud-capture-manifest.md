# Local Metal HUD Capture Manifest

## Purpose

Phase 60Z adds a local-only Metal HUD capture manifest for future Dock/transparency/blur frame pacing analysis.

The target remains RTX 5070 only.

Fallback GPU substitution is not accepted as RTX 5070 proof.

This phase creates a capture manifest only.

This phase does not enable Metal HUD.

This phase does not run a Metal workload.

This phase does not capture a Metal workload.

This phase does not generate a Metal performance report.

This phase does not claim RTX 5070 acceleration.

This phase does not claim RTX 5070 UI smoothness.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration proof.

## Capture Manifest Scope

The manifest links:

- scenario marker aggregation
- Dock/transparency/blur scenarios
- future Metal HUD report path
- future frame pacing fields
- future RTX 5070 attribution fields
- safety flags proving this phase did not run GPU work

## Required Future Scenarios

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

## Required Future HUD Metrics

- fps_avg
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
- scenario_marker_duration_seconds
- before_after_delta

## Required Future Attribution Fields

- scenario_marker_timing
- metal_hud_report_timing
- windowserver_attribution
- core_animation_attribution
- quartzcore_attribution
- metal_compositor_attribution
- rtx5070_attribution
- fallback_gpu_attribution
- spoofed_metal_support_false

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

This phase does not enable Metal HUD.

This phase does not run a Metal workload.

This phase does not generate a Metal performance report.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Next Gate

Phase 61A should add a local Metal HUD environment capture preparation gate.

Phase 61A must still not submit RTX 5070 GPU commands or claim acceleration.

## Classification

- CLASSIFICATION_LOCAL_METAL_HUD_CAPTURE_MANIFEST
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_CAPTURE_MANIFEST_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
