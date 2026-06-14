# XcodeProj Materialization Helper

## Purpose

Phase 60N adds a hard opt-in local helper for materializing the missing Xcode project path:

- apps/H1mekaRTXDriverKit/H1mekaRTXDriverKit.xcodeproj

Phase 60M created the source/config/manual inputs, but the actual .xcodeproj still does not exist.

This helper is intentionally conservative.

By default it refuses to generate anything.

CI must not generate a project.

CI must not run xcodebuild.

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

## Helper Strategy

The helper supports two modes:

1. `--emit-xcodegen-spec`

Writes a local project spec under host-report-bundle only.

2. `--materialize-with-xcodegen`

Runs xcodegen only when installed and hard opt-in flags are present.

If xcodegen is not installed, the helper records a local-only refusal and instructs manual Xcode creation or installing xcodegen separately.

The repo does not vendor xcodegen.

The repo does not commit generated .xcodeproj output in this phase.

## Required Runtime Flags

Actual local materialization is allowed only when all flags are present:

- --i-understand-xcodeproj-materialization
- --output-under-host-report-bundle
- one of:
  - --emit-xcodegen-spec
  - --materialize-with-xcodegen

Optional:

- --replace-existing
- --project-path apps/H1mekaRTXDriverKit/H1mekaRTXDriverKit.xcodeproj

## Runtime Boundary

Even if .xcodeproj is created locally:

- Phase 60L must prove a real Xcode-built DriverKit dext binary
- signing/preflight must be rerun
- /Applications activation remediation must be rerun
- provider open remains blocked
- IOServiceOpen remains blocked
- BAR mapping remains blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_XCODEPROJ_MATERIALIZATION_HELPER
- CLASSIFICATION_XCODE_DRIVERKIT_PROJECT_MATERIALIZATION_PLAN
- CLASSIFICATION_LOCAL_PROJECT_HELPER_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
