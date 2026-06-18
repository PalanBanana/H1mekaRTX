# DriverKit Entitlement Request Notes Template

## Project

- Project: H1mekaRTX
- Target GPU: NVIDIA RTX 5070
- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de

## Bundle Identifiers

- Host App Bundle ID: dev.h1meka.H1mekaRTXHost
- DriverKit Bundle ID: dev.h1meka.H1mekaRTXDriver

## Requested Scope Placeholder

- DriverKit base entitlement: pending / not requested by this phase
- PCI transport entitlement: pending / not requested by this phase
- Provider open permission: not requested by this phase
- UserClient access: pending / not requested by this phase

## Safety Evidence

- No provider open has been performed.
- No IOServiceOpen has been performed.
- No BAR mapping has been performed.
- No BAR0 read has been performed.
- No BAR0 write has been performed.
- No GPU command submission has been performed.
- No Metal acceleration proof is claimed.
- No Dock/transparency/blur acceleration proof is claimed.

## Review Notes

This is a package skeleton only. Do not submit as-is without real Apple Developer account/team details and entitlement-request context.
