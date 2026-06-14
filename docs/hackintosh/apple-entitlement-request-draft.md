# Apple Entitlement Request Draft

## Product / Project

H1mekaRTX

## Developer Team

`<APPLE_TEAM_ID>`

## Host App Bundle ID

`dev.h1meka.H1mekaRTXHost`

## Driver Extension Bundle ID

`dev.h1meka.H1mekaRTXDriver`

## Requested Capabilities / Entitlements

- DriverKit
- PCIDriverKit PCI transport
- System Extension
- DriverKit communicates with drivers

## Target Hardware

- Hardware: NVIDIA RTX 5070
- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Subsystem Vendor ID: `0x1458`
- Subsystem ID: `0x417e`

## Request Reason

The H1mekaRTX project is building a user-space DriverKit research driver for an RTX 5070 PCI device on macOS.

The immediate goal is to establish a legitimate DriverKit / PCIDriverKit development path for provider matching, entitlement validation, and local-only diagnostics.

The long-term research goal is to evaluate whether RTX 5070 can be attributed to UI compositor and Metal-related graphics acceleration evidence under macOS without spoofing or fallback GPU substitution.

## Safety Commitments

The initial approved entitlement usage will remain read-only and default-deny.

The project will not perform BAR/MMIO writes, PCI configuration writes, firmware loading, GPU reset, display-engine initialization, framebuffer initialization, or GPU command submission until separate internal hard-opt-in gates and safety reviews pass.

The project will not bypass SIP, AMFI, Gatekeeper, or code signing.

The project will not patch WindowServer.

The project will not claim RTX 5070 Metal acceleration or Dock/transparency/blur acceleration without attribution evidence.

## Evidence Already Available

- RTX 5070 target identity matrix.
- Local read-only RTX 5070 UI baseline collector.
- Dock/transparency/blur scenario marker.
- Scenario marker aggregation.
- Metal HUD / frame pacing capture plan.
- Local Metal HUD capture manifest.
- Local Metal HUD environment prep.
- Local Metal HUD hard-opt-in capture wrapper.
- RTX 5070 accelerated bring-up critical path gate.

## Requested Approval

Please enable DriverKit and PCIDriverKit PCI transport development entitlement access for the above driver extension and host app identifiers so the project can proceed with legitimate provider matching and local diagnostics.

## Exact Excluded Initial Usage Terms

The following exact terms are intentionally included for release-readiness validation and Apple request clarity:

- BAR/MMIO writes
- PCI configuration writes
- GPU command submission
- Metal acceleration claims
- Dock/transparency/blur acceleration claims

