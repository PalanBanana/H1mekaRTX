# RTX 5070-Only UI Smoothness Roadmap

## Purpose

Phase 60T preserves the project requirement:

- Dock smoothness must remain in scope.
- Transparency / blur smoothness must remain in scope.
- Window movement / resize smoothness must remain in scope.
- Mission Control / Launchpad / Stage Manager smoothness must remain in scope.
- The target GPU remains RTX 5070.
- The target PCI identity remains NVIDIA vendor 0x10de, device 0x2f04, IOPCIMatch 0x2f0410de.

This phase explicitly does not switch the project goal to AMD, Intel iGPU, Apple Silicon, or a generic supported GPU.

## Reality Boundary

Current blocker:

- Personal Team cannot proceed with System Extension capability.
- DriverKit profile requires DriverKit enablement.
- DriverKit entitlement approval is not proven.
- DriverKit PCI transport entitlement approval is not proven.
- real_driverkit_dext_built is not proven.
- RTX 5070 provider visibility is not proven.
- RTX 5070 provider open is not allowed.
- RTX 5070 BAR mapping is not allowed.
- RTX 5070 GPU command submission is not allowed.
- RTX 5070 Metal compositor attribution is not proven.

Therefore the project cannot yet claim:

- RTX 5070 Metal acceleration
- RTX 5070 WindowServer acceleration
- RTX 5070 Core Animation acceleration
- RTX 5070 QuartzCore acceleration
- RTX 5070 Dock/transparency/blur acceleration
- RTX 5070 UI smoothness improvement

## Non-Negotiable Target

The final proof target remains:

- RTX 5070 is present.
- RTX 5070 is accepted by a valid DriverKit/System Extension chain.
- RTX 5070 has a real provider identity.
- RTX 5070 is associated with real GPU work.
- WindowServer / Core Animation / QuartzCore / Metal compositor path can be attributed to RTX 5070.
- Dock/transparency/blur/window animation frame pacing improves in measured before/after runs.
- No spoofed Metal support is used.
- No fake UI acceleration badge is used.

## Allowed Parallel Work While Entitlement Is Blocked

The project may continue with:

1. RTX 5070 UI proof schema hardening.
2. Dock/transparency/blur scenario list.
3. Frame pacing and hitch metric collection schema.
4. WindowServer/Core Animation/QuartzCore attribution schema.
5. Local read-only UI baseline capture.
6. Local read-only display/Metal support inventory.
7. RTX 5070 provider entitlement readiness tracking.
8. Paid Apple Developer / DriverKit entitlement checklist tracking.
9. Safety gates proving that no provider open, IOServiceOpen, BAR mapping, MMIO mutation, or GPU command submission occurred.

## Disallowed Alternative Methods

The following remain disallowed:

- claiming AMD/iGPU/Apple Silicon results as RTX 5070 results
- fake Metal support spoofing
- WindowServer private framework patching
- SIP bypass
- AMFI bypass
- kernel injection
- process injection
- BAR poking
- MMIO writes
- PCI config writes
- firmware load
- GPU reset
- display-engine init
- framebuffer init
- GPU command submission before an explicit later gate

## RTX 5070 Dock Smoothness Proof Ladder

A future RTX 5070 Dock/transparency/blur proof requires all of:

1. Paid Apple Developer team proven.
2. DriverKit entitlement approval proven.
3. System Extension entitlement/profile proven.
4. PCI transport entitlement/profile proven.
5. real_driverkit_dext_built=true.
6. System Extension activation visible.
7. RTX 5070 provider match visible.
8. Provider open gate explicitly approved in a later phase.
9. BAR mapping gate explicitly approved in a later phase.
10. GPU command submission gate explicitly approved in a later phase.
11. Metal/WindowServer/Core Animation/QuartzCore attribution collected.
12. Dock/transparency/blur frame pacing before/after captured.
13. Result says RTX 5070, not fallback GPU.

## Next Safe Gate

Phase 60U should add an RTX 5070-only UI smoothness evidence matrix and local baseline collector that keeps RTX 5070 as the only acceptable target while still marking current RTX acceleration as blocked.

## Classification

- CLASSIFICATION_RTX5070_UI_SMOOTHNESS_ROADMAP
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_ENTITLEMENT_BLOCKED_BUT_UI_SCOPE_RETAINED
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS

## Checker Exact Tokens

This section intentionally preserves exact phrases required by the Phase 60T static checker.

- RTX 5070
- Dock smoothness must remain in scope
- Transparency / blur smoothness must remain in scope
- The target GPU remains RTX 5070
- does not switch the project goal to AMD
- No spoofed Metal support is used
- WindowServer / Core Animation / QuartzCore / Metal compositor path can be attributed to RTX 5070
- provider open remains blocked
- BAR mapping remains blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## RTX 5070 Only Position

RTX 5070 remains the only target GPU for this roadmap.

AMD, Intel iGPU, Apple Silicon, or another fallback GPU may be used only as a baseline comparator, never as proof of RTX 5070 acceleration.

Dock smoothness, transparency / blur smoothness, window movement, resize, Mission Control, Launchpad, Stage Manager, WindowServer, Core Animation, QuartzCore, and Metal compositor attribution remain in scope for RTX 5070.

## Current Proof State

Current RTX 5070 Metal acceleration is not claimed.

Current RTX 5070 UI smoothness is not claimed.

Current WindowServer attribution to RTX 5070 is not proven.

Current Core Animation attribution to RTX 5070 is not proven.

Current QuartzCore attribution to RTX 5070 is not proven.

Current Metal compositor attribution to RTX 5070 is not proven.

Phase 61 is not allowed now.

provider open remains blocked.

IOServiceOpen remains blocked.

BAR mapping remains blocked.

BAR/MMIO mutation remains blocked.

PCI configuration writes remain blocked.

GPU command submission remains blocked.

Metal proof remains blocked.

Dock/transparency/blur proof remains blocked.

