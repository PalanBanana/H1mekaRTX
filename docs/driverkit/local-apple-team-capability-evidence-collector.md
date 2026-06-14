# Local Apple Team Capability Evidence Collector

## Purpose

Phase 60S adds a local-only evidence collector for Apple account/team/provisioning capability state.

Phase 60Q and Phase 60R established that the current blocker is not source code, XcodeGen, or DriverKit SDK availability.

The current blocker is Apple Developer team/provisioning capability:

- Personal Team cannot support System Extension capability.
- DriverKit profile cannot be requested until DriverKit is enabled.
- DriverKit entitlement approval is not proven.
- DriverKit PCI transport entitlement approval is not proven.
- Host and dext provisioning profiles are missing.

This phase collects local evidence only.

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

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Local Evidence Inputs

The collector may read:

- host-report-bundle/real-driverkit-build/xcodebuild-allow-provisioning.log
- host-report-bundle/real-driverkit-build/real-driverkit-dext-build-gate-report.json
- release-readiness/provisioning-entitlement-hardblock-gate-check.json
- release-readiness/apple-developer-entitlement-request-checklist-check.json

The collector may run read-only/status-only commands:

- xcodebuild -version
- xcrun --sdk driverkit --show-sdk-path
- xcrun --sdk macosx --show-sdk-path
- security find-identity -v -p codesigning
- xcodebuild -list -project apps/H1mekaRTXDriverKit/H1mekaRTXDriverKit.xcodeproj
- xcodebuild -showBuildSettings -project apps/H1mekaRTXDriverKit/H1mekaRTXDriverKit.xcodeproj -scheme H1mekaRTXHost -configuration Debug

## Sanitization

Raw command stdout/stderr remains local-only under host-report-bundle.

Committed release-readiness output must contain only sanitized booleans and blocker categories.

## Evidence Categories

The summary records whether local evidence indicates:

- Apple Development signing identity present
- Xcode present
- DriverKit SDK present
- macOS SDK present
- Xcode project present
- Personal Team blocker observed
- System Extension capability blocker observed
- DriverKit enablement blocker observed
- Host provisioning profile missing
- Dext provisioning profile missing
- Paid Developer Team proven
- DriverKit entitlement approval proven
- PCI transport entitlement approval proven

## Continued Runtime Boundary

Even if evidence is collected:

- Phase 61 remains blocked
- provider open remains blocked
- IOServiceOpen remains blocked
- BAR mapping remains blocked
- BAR/MMIO mutation remains blocked
- PCI configuration writes remain blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_LOCAL_APPLE_TEAM_CAPABILITY_EVIDENCE
- CLASSIFICATION_APPLE_DEVELOPER_ENTITLEMENT_REQUEST_CHECKLIST
- CLASSIFICATION_LOCAL_EVIDENCE_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
