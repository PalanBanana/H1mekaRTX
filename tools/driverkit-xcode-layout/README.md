# Deterministic Xcode / DriverKit Project Layout

This directory contains static layout metadata only.

It does not generate an `.xcodeproj`, build, sign, install, activate, load a dext, open a provider, map BAR memory, or submit GPU commands.

## Files

- `project-layout.json`

## Future target layout

- Project: `H1mekaRTXDriverKit`
- Host target: `H1mekaRTXHost`
- Dext target: `H1mekaRTXDriver`

## Safety

This is a layout contract only. It preserves the RTX 5070 macOS UI compositor goal without claiming Dock, transparency, blur, WindowServer, Core Animation, QuartzCore, Metal compositor, UI compositor proof, or Metal proof success.
