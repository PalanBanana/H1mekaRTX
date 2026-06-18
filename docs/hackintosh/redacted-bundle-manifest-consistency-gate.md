# Redacted Bundle Manifest Consistency Gate

Phase 63C adds a redacted bundle manifest consistency gate.

This phase is redacted-consistency-gate-only.

This phase does not create an export archive.

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

## Consistency Requirements

- RTX 5070 vendor ID: `0x10de`
- RTX 5070 device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Host app bundle identifier: `dev.h1meka.H1mekaRTXHost`
- DriverKit bundle identifier: `dev.h1meka.H1mekaRTXDriver`
- Redacted manifest exists
- Export bundle archive is not created
- Secrets and provisioning assets are not exported
- Provider open and BAR access remain blocked
- GPU command submission remains blocked
- Metal acceleration is not claimed
- Dock/transparency/blur acceleration is not claimed

## Next Gate

Phase 63D should add a redacted export bundle dry-run plan.
