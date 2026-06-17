# Read-Only Provider Visibility Command Generator

## Purpose

Phase 62G generates local read-only command templates for checking whether the RTX 5070 DriverKit/PCIDriverKit provider may be visible in IORegistry-style outputs.

This phase is command-template-only.

This phase does not execute provider visibility commands.

This phase does not open a provider.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not read BAR0.

This phase does not write BAR0.

This phase does not mutate BAR/MMIO.

This phase does not submit GPU commands.

This phase does not claim RTX 5070 Metal acceleration.

This phase does not claim Dock/transparency/blur acceleration.

## RTX 5070 Match Target

- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Subsystem Vendor ID: `0x1458`
- Subsystem ID: `0x417e`
- Expected DriverKit Bundle ID: `dev.h1meka.H1mekaRTXDriver`

## Generated Read-Only Commands

The generated commands are intended for a later manual local run only.

They are limited to read-only discovery commands such as:

- `ioreg` tree inspection
- `systemextensionsctl list`
- `kmutil showloaded`
- `log show` filtering for DriverKit/SystemExtension messages

The generated command file must not include:

- `IOServiceOpen`
- `ioreg -w` mutation
- `nvram`
- `kextload`
- `kmutil load`
- BAR mapping
- BAR0 read/write
- MMIO write
- PCI config write
- firmware loading
- GPU reset
- GPU command submission

## Current State

Current RTX 5070 Metal acceleration is not proven.

Current RTX 5070 UI smoothness is not proven.

Provider visibility command execution is not performed by this phase.

Provider open remains blocked.

IOServiceOpen remains blocked.

BAR mapping remains blocked.

BAR0 read remains blocked.

BAR0 write remains blocked.

GPU command submission remains blocked.

Framebuffer/display path remains blocked.

Metal compositor attribution remains blocked.

Dock/transparency/blur proof remains blocked.

## Next Gate

Phase 62H should add a local read-only provider visibility capture wrapper with hard opt-in.

Phase 62H must still not open a provider.

## Classification

- CLASSIFICATION_READONLY_PROVIDER_VISIBILITY_COMMAND_GENERATOR
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_COMMAND_TEMPLATE_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
