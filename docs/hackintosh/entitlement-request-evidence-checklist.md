# Entitlement Request Evidence Checklist

Phase 62W adds an entitlement request evidence checklist.

This phase is evidence-checklist-only.

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

- `release-readiness/entitlement-request-package-skeleton.json`
- `release-readiness/entitlement-request-package-skeleton-check.json`
- `docs/hackintosh/driverkit-entitlement-request-notes-template.md`
- `release-readiness/noopen-to-entitlement-request-handoff-ledger.json`

## Evidence Checklist

The future real entitlement request should include:

- Apple Developer team/account holder details
- Host app bundle identifier
- DriverKit extension bundle identifier
- DriverKit base entitlement request scope
- PCI transport entitlement request scope
- RTX 5070 vendor ID
- RTX 5070 device ID
- IOPCIMatch
- no-open provider-match readiness evidence
- BAR safety evidence
- no GPU command submission evidence
- no Metal acceleration claim
- no Dock/transparency/blur claim

## Required Placeholders

- Team ID placeholder
- App ID placeholder
- Request form status placeholder
- DriverKit entitlement status placeholder
- PCI transport entitlement status placeholder
- Development provisioning profile status placeholder
- Review notes placeholder

## Explicit Non-Claims

This checklist does not prove entitlement approval.

This checklist does not prove provisioning profile creation.

This checklist does not prove DriverKit extension activation.

This checklist does not prove provider open.

This checklist does not prove BAR access.

This checklist does not prove GPU command submission.

This checklist does not prove RTX 5070 Metal acceleration.

This checklist does not prove Dock/transparency/blur acceleration.

## Next Gate

Phase 62X should add the entitlement request package consistency gate.

Phase 62X must still not submit the entitlement request or open a provider.
