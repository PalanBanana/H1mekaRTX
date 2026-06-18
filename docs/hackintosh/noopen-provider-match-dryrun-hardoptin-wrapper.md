# No-Open Provider Match Dry-Run Hard-Opt-In Wrapper

Phase 62P adds a hard-opt-in wrapper for no-open provider match dry-run command templates.

This phase defaults to refusal.

This phase does not open a provider.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not read BAR0.

This phase does not write BAR0.

This phase does not mutate BAR/MMIO.

This phase does not submit GPU commands.

This phase does not claim RTX 5070 Metal acceleration.

This phase does not claim Dock/transparency/blur acceleration.

## Hard Opt-In

The wrapper executes no-open dry-run command templates only when this exact environment variable is present:

`H1MEKARTX_ALLOW_NOOPEN_PROVIDER_MATCH_DRYRUN=I_UNDERSTAND_NOOPEN_PROVIDER_MATCH_DRYRUN_ONLY`

## Input Manifest

- `release-readiness/noopen-provider-match-dryrun-command-manifest.json`

## Local-Only Raw Output

If manually opted in, raw local output is written under:

`host-report-bundle/noopen-provider-match-dryrun/`

That directory must not be committed.

## Allowed Actions

- read-only IORegistry grep
- read-only system extension listing
- read-only DriverKit log filtering
- local sanitized summary inspection

## Forbidden Actions

- provider open
- IOServiceOpen
- BAR mapping
- BAR0 read
- BAR0 write
- BAR/MMIO mutation
- PCI configuration writes
- firmware loading
- GPU reset
- framebuffer/display-engine init
- GPU command submission
- Metal proof claim
- Dock/transparency/blur acceleration claim

## RTX 5070 Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de
- Expected DriverKit Bundle ID: dev.h1meka.H1mekaRTXDriver

## Next Gate

Phase 62Q should add a sanitized no-open provider match dry-run output parser.

Phase 62Q must still not open a provider.
