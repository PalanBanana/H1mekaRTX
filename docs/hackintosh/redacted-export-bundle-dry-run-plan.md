# Redacted Export Bundle Dry-Run Plan

Phase 63D adds a redacted export bundle dry-run plan.

This phase is dry-run-plan-only.

This phase does not create an export archive.

This phase does not copy files into an export bundle.

This phase does not export provisioning assets.

This phase does not export certificates.

This phase does not export private keys.

This phase does not export raw IORegistry data.

This phase does not export provider handles.

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

- `release-readiness/redacted-bundle-manifest-consistency-gate.json`
- `release-readiness/redacted-bundle-manifest-consistency-gate-check.json`
- `release-readiness/redacted-manual-export-bundle-manifest.json`
- `release-readiness/manual-entitlement-request-packet-export-checklist.json`

## Dry-Run Plan

The future dry-run export plan should only enumerate these redacted artifacts:

- `docs/hackintosh/driverkit-entitlement-request-notes-template.md`
- `release-readiness/entitlement-request-package-skeleton.md`
- `release-readiness/entitlement-request-evidence-checklist.md`
- `release-readiness/entitlement-request-package-consistency-gate.md`
- `release-readiness/entitlement-request-pre-submission-packet-ledger.md`
- `release-readiness/entitlement-request-local-submission-readiness-gate.md`
- `release-readiness/manual-entitlement-request-packet-export-checklist.md`
- `release-readiness/redacted-manual-export-bundle-manifest.md`
- `release-readiness/redacted-bundle-manifest-consistency-gate.md`

## Dry-Run Exclusions

The future dry-run export plan must still exclude:

- host report bundles
- raw stdout/stderr
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

Phase 63E should add a redacted export dry-run plan consistency gate.

Phase 63E must still not create a real archive, export secrets, submit the entitlement request, or open a provider.
