# Sanitized Local Provider Visibility Capture Parser

## Purpose

Phase 62I adds a sanitized parser for local read-only provider visibility captures.

This phase is parser-only by default.

This phase does not execute provider visibility commands.

This phase does not open a provider.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not read BAR0.

This phase does not write BAR0.

This phase does not mutate BAR/MMIO.

This phase does not submit GPU commands.

This phase does not claim RTX 5070 Metal acceleration.

This phase does not claim Dock/transparency/blur acceleration.

## Input

Optional local-only raw capture path:

`host-report-bundle/readonly-provider-visibility/readonly-provider-visibility-local-capture.json`

That raw file must not be committed.

## Opt-In

Default behavior refuses parsing of raw local capture.

Parsing a raw local capture requires:

`H1MEKARTX_PARSE_LOCAL_PROVIDER_VISIBILITY_CAPTURE=I_UNDERSTAND_SANITIZED_READONLY_PROVIDER_VISIBILITY_PARSE_ONLY`

## Sanitized Output

The parser may write sanitized summary files under:

- `release-readiness/sanitized-local-provider-visibility-capture-parser-summary.json`
- `release-readiness/sanitized-local-provider-visibility-capture-parser-summary.md`

The sanitized output may contain:

- capture decision
- hard opt-in state
- command count
- command names
- command return codes
- detected token booleans
- blocked operation booleans

The sanitized output must not contain:

- raw stdout
- raw stderr
- private user paths
- full logs
- hardware write data
- BAR contents
- MMIO contents

## RTX 5070 Target

- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Expected DriverKit Bundle ID: `dev.h1meka.H1mekaRTXDriver`

## Current State

Current RTX 5070 Metal acceleration is not proven.

Current RTX 5070 UI smoothness is not proven.

Provider open remains blocked.

IOServiceOpen remains blocked.

BAR mapping remains blocked.

BAR0 read remains blocked.

BAR0 write remains blocked.

GPU command submission remains blocked.

Framebuffer/display path remains blocked.

Metal compositor attribution remains blocked.

Dock/transparency/blur proof remains blocked.

## Next Gate

Phase 62J should add a sanitized provider visibility evidence matrix.

Phase 62J must still not open a provider.

## Classification

- CLASSIFICATION_SANITIZED_LOCAL_PROVIDER_VISIBILITY_CAPTURE_PARSER
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_PARSE_ONLY_DEFAULT_REFUSAL
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
