# Local Opt-In Provider Visibility Evidence Capture Runbook

## Purpose

Phase 62K adds a local opt-in runbook for collecting sanitized RTX 5070 provider visibility evidence.

This phase is runbook-only.

This phase does not execute provider visibility capture.

This phase does not parse raw capture.

This phase does not open a provider.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not read BAR0.

This phase does not write BAR0.

This phase does not mutate BAR/MMIO.

This phase does not submit GPU commands.

This phase does not claim RTX 5070 Metal acceleration.

This phase does not claim Dock/transparency/blur acceleration.

## RTX 5070 Target

- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Expected DriverKit Bundle ID: `dev.h1meka.H1mekaRTXDriver`

## Manual Local Capture Procedure

Only run this manually on a local machine when read-only provider visibility evidence is desired.

### Step 1: run read-only provider visibility capture

```bash
cd /Users/h1meka/Dev/H1mekaRTX
H1MEKARTX_ALLOW_READONLY_PROVIDER_VISIBILITY=I_UNDERSTAND_READONLY_PROVIDER_VISIBILITY_ONLY \
python3 scripts/capture-local-readonly-provider-visibility.py
```

### Step 2: parse sanitized provider visibility evidence

```bash
cd /Users/h1meka/Dev/H1mekaRTX
H1MEKARTX_PARSE_LOCAL_PROVIDER_VISIBILITY_CAPTURE=I_UNDERSTAND_SANITIZED_READONLY_PROVIDER_VISIBILITY_PARSE_ONLY \
python3 scripts/parse-sanitized-local-provider-visibility-capture.py
```

### Step 3: rebuild sanitized evidence matrix

```bash
cd /Users/h1meka/Dev/H1mekaRTX
python3 scripts/build-sanitized-provider-visibility-evidence-matrix.py
python3 scripts/check-sanitized-provider-visibility-evidence-matrix.py
```

## Expected Local-Only Raw Output

Raw capture may exist only under:

`host-report-bundle/readonly-provider-visibility/`

That directory must not be committed.

## Allowed Committed Outputs

Only sanitized outputs may be committed:

- `release-readiness/sanitized-local-provider-visibility-capture-parser-summary.json`
- `release-readiness/sanitized-local-provider-visibility-capture-parser-summary.md`
- `release-readiness/sanitized-provider-visibility-evidence-matrix.json`
- `release-readiness/sanitized-provider-visibility-evidence-matrix.md`

## Forbidden

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

## Current State

Current RTX 5070 Metal acceleration is not proven.

Current RTX 5070 UI smoothness is not proven.

Provider visibility evidence is not provider open.

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

Phase 62L should add a sanitized provider visibility evidence promotion gate.

Phase 62L must still not open a provider.

## Classification

- CLASSIFICATION_LOCAL_OPTIN_PROVIDER_VISIBILITY_EVIDENCE_CAPTURE_RUNBOOK
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_RUNBOOK_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
