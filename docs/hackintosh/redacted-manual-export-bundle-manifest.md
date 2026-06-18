# Redacted Manual Export Bundle Manifest

Phase 63B adds a redacted manual export bundle manifest.

This phase is redacted-manifest-only.

This phase does not create an export archive.

This phase does not export provisioning assets.

This phase does not export certificates.

This phase does not export private keys.

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

- `release-readiness/manual-entitlement-request-packet-export-checklist.json`
- `release-readiness/manual-entitlement-request-packet-export-checklist-check.json`
- `release-readiness/entitlement-request-local-submission-readiness-gate.json`
- `release-readiness/entitlement-request-pre-submission-packet-ledger.json`
- `release-readiness/entitlement-request-evidence-checklist.json`
- `docs/hackintosh/driverkit-entitlement-request-notes-template.md`

## Redacted Bundle Manifest Contents

The future manual bundle may include these redacted files:

- DriverKit entitlement request notes template
- entitlement request package skeleton summary
- entitlement request evidence checklist summary
- entitlement request package consistency gate summary
- entitlement request pre-submission packet ledger summary
- entitlement request local submission readiness gate summary
- manual entitlement request packet export checklist summary

## Always Exclude

- raw stdout/stderr captures
- private local paths
- certificates
- private keys
- provisioning profiles
- Apple account email unless manually approved
- Team ID unless manually approved
- device serial numbers
- raw IORegistry dumps
- BAR/MMIO data
- provider handles
- kernel logs containing private paths

## Next Gate

Phase 63C should add a redacted bundle manifest consistency gate.

Phase 63C must still not submit the entitlement request or open a provider.
