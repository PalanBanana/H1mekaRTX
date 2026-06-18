# Sanitized No-Open Provider Match Dry-Run Output Parser

Phase 62Q adds a sanitized parser for no-open provider match dry-run output.

This phase is parser-only by default.

This phase does not execute provider match dry-run commands.

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

Optional local-only raw capture:

`host-report-bundle/noopen-provider-match-dryrun/noopen-provider-match-dryrun-local-capture.json`

That file must not be committed.

## Hard Opt-In

Default behavior refuses parsing.

Parsing requires:

`H1MEKARTX_PARSE_NOOPEN_PROVIDER_MATCH_DRYRUN_OUTPUT=I_UNDERSTAND_SANITIZED_NOOPEN_PROVIDER_MATCH_DRYRUN_PARSE_ONLY`

## Sanitized Output

Committed sanitized output may contain:

- decision
- hard opt-in state
- command count
- command IDs
- command return codes
- token detection booleans
- blocked operation booleans

Committed sanitized output must not contain:

- raw stdout
- raw stderr
- private user paths
- full logs
- BAR contents
- MMIO contents

## RTX 5070 Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de
- Expected DriverKit Bundle ID: dev.h1meka.H1mekaRTXDriver

## Next Gate

Phase 62R should add no-open dry-run evidence matrix aggregation.

Phase 62R must still not open a provider.
