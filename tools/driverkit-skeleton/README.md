# H1mekaRTX Non-Activating DriverKit Skeleton

This directory contains static templates only.

It is intentionally not a buildable, signed, installable, or activatable DriverKit project yet.

## Included templates

- `H1mekaRTXHost.app.template/Info.plist`
- `H1mekaRTXDriver.dext.template/Info.plist`

## Safety

This skeleton does not:

- build
- sign
- install
- activate a System Extension
- load a dext
- request device ownership
- open an IOPCIDevice provider
- map BAR memory
- write MMIO
- reset GPU
- load GSP firmware
- initialize framebuffer
- initialize display engine
- submit GPU commands
- claim Dock / transparency / blur / Metal acceleration

## Target

Future RTX 5070 macOS UI compositor research path:

- WindowServer
- Core Animation
- QuartzCore
- Metal compositor
- IOGraphics
- IOAccelerator
- IODisplay
