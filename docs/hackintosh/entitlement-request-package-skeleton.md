# Entitlement Request Package Skeleton

Phase 62V adds an entitlement request package skeleton.

This phase is package-skeleton-only.

This phase does not submit an Apple entitlement request.

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

- `release-readiness/noopen-to-entitlement-request-handoff-ledger.json`
- `release-readiness/noopen-to-entitlement-request-handoff-ledger-check.json`
- optional existing entitlement request package docs from earlier phases

## Apple-Side Package Skeleton

The package skeleton tracks fields that will be needed for a future real Apple request:

- Account holder / team placeholder
- App ID placeholder
- Host app bundle identifier: `dev.h1meka.H1mekaRTXHost`
- DriverKit bundle identifier: `dev.h1meka.H1mekaRTXDriver`
- DriverKit entitlement placeholder
- PCI transport entitlement placeholder
- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- No-open provider match readiness proof
- BAR safety proof
- No Metal acceleration claim

## Explicit Non-Claims

This package skeleton does not prove entitlement approval.

This package skeleton does not prove provisioning profile creation.

This package skeleton does not prove DriverKit extension activation.

This package skeleton does not prove provider open.

This package skeleton does not prove BAR access.

This package skeleton does not prove GPU command submission.

This package skeleton does not prove RTX 5070 Metal acceleration.

This package skeleton does not prove Dock/transparency/blur acceleration.

## Next Gate

Phase 62W should add entitlement request evidence checklist.

Phase 62W must still not request entitlements or open a provider.
