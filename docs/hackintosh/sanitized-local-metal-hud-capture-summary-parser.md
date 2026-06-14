# Sanitized Local Metal HUD Capture Summary Parser

## Purpose

Phase 61D adds a sanitized parser for local-only Metal HUD hard-opt-in capture reports.

The target remains RTX 5070 only.

Fallback GPU substitution is not accepted as RTX 5070 proof.

This phase parses local reports only.

This phase does not execute the capture wrapper.

This phase does not enable Metal HUD.

This phase does not run a Metal workload.

This phase does not capture a Metal workload.

This phase does not generate a Metal performance report.

This phase does not claim RTX 5070 acceleration.

This phase does not claim RTX 5070 UI smoothness.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration proof.

## Parser Inputs

Local-only input:

- host-report-bundle/local-metal-hud-hardoptin-capture/local-metal-hud-hardoptin-capture-report.json
- host-report-bundle/local-metal-hud-hardoptin-capture/raw/*.stdout.txt
- host-report-bundle/local-metal-hud-hardoptin-capture/raw/*.stderr.txt
- host-report-bundle/local-metal-hud-hardoptin-capture/raw/*.metal-hud.log

Committed input:

- tools/hackintosh/local-metal-hud-hardoptin-capture-wrapper.json
- release-readiness/local-metal-hud-hardoptin-capture-summary.json
- tools/hackintosh/local-metal-hud-dryrun-launch-command-generator.json

## Sanitized Output

Committed output may contain only:

- report presence
- decision
- scenario name
- duration seconds
- process return code
- sanitized counts
- Metal HUD env key names
- raw file presence booleans
- raw file size byte counts
- parsed metric token counts
- proof flags set to false

Committed output must not contain:

- raw stdout
- raw stderr
- raw Metal HUD logs
- private paths
- target app path
- environment values
- e-mail addresses
- hashes
- signing identities

## Current Proof State

Current RTX 5070 Metal acceleration is not claimed.

Current RTX 5070 UI smoothness is not claimed.

Current WindowServer attribution to RTX 5070 is not proven.

Current Core Animation attribution to RTX 5070 is not proven.

Current QuartzCore attribution to RTX 5070 is not proven.

Current Metal compositor attribution to RTX 5070 is not proven.

Current Dock/transparency/blur acceleration proof is not proven.

Phase 61E is not allowed now.

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

This phase does not execute the Metal HUD wrapper.

This phase does not enable Metal HUD.

This phase does not run a Metal workload.

This phase does not capture a Metal workload.

This phase does not generate a Metal performance report.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Next Gate

Phase 61E should add a local Metal HUD report metric schema.

Phase 61E must still not claim RTX 5070 acceleration unless RTX 5070 attribution is proven.

## Classification

- CLASSIFICATION_SANITIZED_LOCAL_METAL_HUD_CAPTURE_SUMMARY_PARSER
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_SANITIZED_PARSER_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
