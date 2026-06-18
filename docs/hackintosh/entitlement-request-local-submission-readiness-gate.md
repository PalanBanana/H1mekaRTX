# Entitlement Request Local Submission Readiness Gate

Phase 62Z adds a local submission readiness gate for the entitlement request packet.

This phase is local-readiness-gate-only.

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

- `release-readiness/entitlement-request-pre-submission-packet-ledger.json`
- `release-readiness/entitlement-request-pre-submission-packet-ledger-check.json`
- `release-readiness/entitlement-request-package-consistency-gate.json`
- `release-readiness/entitlement-request-evidence-checklist.json`
- `docs/hackintosh/driverkit-entitlement-request-notes-template.md`

## Local Readiness Meaning

Local readiness means the packet is ready for a human to review before any Apple Developer portal action.

Local readiness does not mean submission.

Local readiness does not mean approval.

Local readiness does not mean App ID creation.

Local readiness does not mean profile creation.

Local readiness does not mean DriverKit extension activation.

Local readiness does not mean provider open.

Local readiness does not mean BAR access.

Local readiness does not mean GPU command submission.

Local readiness does not mean Metal acceleration.

## Required Manual Review Before Any Future Submission

- Confirm Apple Developer account holder/team
- Confirm App ID ownership
- Confirm host app bundle ID
- Confirm DriverKit bundle ID
- Confirm DriverKit entitlement request scope
- Confirm PCI transport entitlement request scope
- Confirm RTX 5070 identity proof
- Confirm no-open safety proof
- Confirm BAR safety proof
- Confirm no GPU command submission proof
- Confirm no Metal acceleration claim
- Confirm no Dock/transparency/blur claim

## RTX 5070 Target

- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Expected DriverKit Bundle ID: `dev.h1meka.H1mekaRTXDriver`
- Expected Host App Bundle ID: `dev.h1meka.H1mekaRTXHost`

## Next Gate

Phase 63A should add a manual entitlement request packet export checklist.

Phase 63A must still not submit the entitlement request or open a provider.
