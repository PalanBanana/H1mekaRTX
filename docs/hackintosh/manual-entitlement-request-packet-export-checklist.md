# Manual Entitlement Request Packet Export Checklist

Phase 63A adds a manual entitlement request packet export checklist.

This phase is manual-export-checklist-only.

This phase does not submit an Apple entitlement request.

This phase does not contact Apple.

This phase does not create an App ID.

This phase does not create a provisioning profile.

This phase does not sign a DriverKit extension.

This phase does not load or activate a DriverKit extension.

This phase does not open a provider.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not read BAR0.

This phase does not write BAR0.

This phase does not mutate BAR/MMIO.

This phase does not submit GPU commands.

This phase does not claim RTX 5070 Metal acceleration.

This phase does not claim Dock/transparency/blur acceleration.

## Inputs

- `release-readiness/entitlement-request-local-submission-readiness-gate.json`
- `release-readiness/entitlement-request-local-submission-readiness-gate-check.json`
- `release-readiness/entitlement-request-pre-submission-packet-ledger.json`
- `release-readiness/entitlement-request-package-consistency-gate.json`
- `release-readiness/entitlement-request-evidence-checklist.json`
- `docs/hackintosh/driverkit-entitlement-request-notes-template.md`

## Manual Export Checklist

Before any real portal action, manually export/review:

- DriverKit entitlement request notes template
- package skeleton
- evidence checklist
- consistency gate output
- pre-submission packet ledger
- local submission readiness gate
- RTX 5070 target proof
- no-open proof
- BAR safety proof
- no GPU command submission proof
- no Metal acceleration claim
- no Dock/transparency/blur claim

## Required Redactions Before Sharing

- Do not export private local paths
- Do not export raw stdout/stderr captures
- Do not export device serial numbers
- Do not export Apple account email unless intentionally provided by the account holder
- Do not export Team ID unless intentionally provided by the account holder
- Do not export provisioning assets
- Do not export certificates or private keys

## Required Manual Fields

- Apple Developer account holder
- Apple Team ID
- App ID
- Host app bundle identifier
- DriverKit extension bundle identifier
- requested DriverKit base entitlement
- requested DriverKit PCI transport entitlement
- review note summary

## RTX 5070 Target

- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Expected DriverKit Bundle ID: `dev.h1meka.H1mekaRTXDriver`
- Expected Host App Bundle ID: `dev.h1meka.H1mekaRTXHost`

## Next Gate

Phase 63B should add a redacted manual export bundle manifest.

Phase 63B must still not submit the entitlement request or open a provider.
