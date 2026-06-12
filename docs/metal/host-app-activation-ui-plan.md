# Host-app Activation UI Plan

## Purpose

Stage 49 adds a host-app activation UI plan.

This is UI-only.

This is not a SwiftUI implementation.

This is not System Extension activation.

This is not activation request creation.

This is not manager submit.

This is not DriverKit target creation.

This is not DriverKit activation.

This is not provider attach.

This is not device ownership.

This is not PCI, BAR, or MMIO access.

This is not RTX 5070 Metal acceleration implementation.

## Decision

Current decision:

    HOST_APP_ACTIVATION_UI_PLAN_READY_UI_ONLY

## Direct Answer

Host-app activation UI planning can start.

All activation and hardware runtime actions remain disabled.

## Planned UI Sections

- StatusOverview
- EvidenceChecklistView
- ActivationGateView
- SafetyBoundaryPanel
- LocalReportImportPlaceholder
- DisabledActionArea

## Disabled UI Actions

The UI may show disabled future controls for:

- Activate Driver
- Deactivate Driver
- Install Driver Extension
- Attach Provider
- Request Device Ownership
- Probe PCI
- Map BAR
- Run Metal Workload On RTX 5070

All of these actions remain disabled.

## Safety Boundary

This stage is UI-plan-only and documentation-only.

It does not create activation request objects, create deactivation request objects, call extension manager submit, implement an activation controller runtime path, create DriverKit targets, add dext provider classes, add Info.plist provider-match dictionaries, activate DriverKit, install DriverKit dexts, request device ownership, attach to PCI providers, query live provider state, query live extension status, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.

## Next Stage

Stage 50 should add a host-app status schema for the UI plan. It must remain local-report-only and must not create activation requests, submit manager requests, create DriverKit targets, attach providers, request device ownership, access PCI config space, map BAR memory, or perform MMIO access.
