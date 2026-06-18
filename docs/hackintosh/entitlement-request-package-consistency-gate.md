# Entitlement Request Package Consistency Gate

Phase 62X adds an entitlement request package consistency gate.

This phase is consistency-gate-only.

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
- `release-readiness/entitlement-request-evidence-checklist.json`
- `release-readiness/entitlement-request-evidence-checklist-check.json`
- `docs/hackintosh/driverkit-entitlement-request-notes-template.md`

## Consistency Requirements

The package skeleton and checklist must agree on:

- RTX 5070 vendor ID: `0x10de`
- RTX 5070 device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Host app bundle identifier: `dev.h1meka.H1mekaRTXHost`
- DriverKit bundle identifier: `dev.h1meka.H1mekaRTXDriver`
- entitlement request not submitted
- Apple not contacted
- App ID not created
- provisioning profile not created
- DriverKit profile not ready
- DriverKit extension not signed, loaded, or activated
- provider open blocked
- IOServiceOpen blocked
- BAR access blocked
- GPU command submission blocked
- Metal acceleration not claimed
- Dock/transparency/blur acceleration not claimed

## Next Gate

Phase 62Y should add an entitlement request pre-submission packet ledger.

Phase 62Y must still not submit the entitlement request or open a provider.
