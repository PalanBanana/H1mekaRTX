# DriverKit Activation Design Review

## Purpose

Stage 16 documents the DriverKit activation design for the full Metal graphics acceleration research track.

This is not a DriverKit activation implementation stage.

This stage does not add a host app target.

This stage does not add a DriverKit dext target.

This stage does not submit a System Extension activation request.

## Decision

Current decision:

    DRIVERKIT_ACTIVATION_DESIGN_ONLY

## Goal

The long-term goal remains full Metal graphics acceleration research for RTX 5070 on macOS.

DriverKit activation is one possible research path for PCI device ownership, but activation is not the same as Metal acceleration.

This stage records the signing, entitlement, provisioning, bundle, and approval gates before any future DriverKit activation attempt.

## Target

- GPU: `NVIDIA RTX 5070`
- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Subsystem Vendor ID: `0x1458`
- Subsystem ID: `0x417e`

## Required Design Areas

- DriverKit entitlement approval
- PCI transport entitlement approval
- Host app system extension install entitlement
- Host app bundle identifier
- Driver extension bundle identifier
- Provisioning profile setup
- Code signing identity setup
- User approval flow
- Provider matching design
- Activation dry-run checklist

## Blockers

- No verified Apple-approved DriverKit PCI entitlement in this repository.
- No host app target exists in this stage.
- No DriverKit dext target exists in this stage.
- No provisioning profile is embedded or referenced in this stage.
- No System Extension activation request code is added in this stage.
- No IOPCIDevice provider ownership is requested in this stage.
- No BAR mapping or MMIO access is allowed in this stage.

## Forbidden Now

- DriverKit activation
- System Extension activation request submission
- IOPCIDevice provider ownership
- PCI config-space reads
- PCI config-space writes
- MMIO reads
- MMIO writes
- BAR memory mapping
- BAR memory poking
- GPU reset logic
- firmware loading
- GSP initialization
- display engine initialization
- framebuffer initialization
- RTX 5070 Metal acceleration attempt
- private graphics framework patching

## Safety Boundary

This stage is read-only.

It does not perform:

- host app target creation
- DriverKit dext target creation
- System Extension activation request submission
- DriverKit activation
- IOPCIDevice ownership request
- ioreg collection
- system_profiler collection
- PCI config-space reads
- PCI config-space writes
- MMIO reads
- MMIO writes
- BAR memory mapping
- BAR memory poking
- GPU reset logic
- firmware loading
- GSP initialization
- display engine initialization
- framebuffer initialization
- RTX 5070 Metal acceleration attempts
- private graphics framework patching

## Notes

DriverKit activation can only be considered after entitlement, provisioning, signing, and user approval requirements are documented and verified.

Even successful DriverKit activation would not automatically mean Metal acceleration works.
