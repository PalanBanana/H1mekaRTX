# Stage 1 DriverKit Plan

## Goal

Create `H1mekaRTXProbe`, a read-only macOS DriverKit/PCIDriverKit experiment that matches RTX 5070 `10de:2f04` and prints PCI/BAR metadata.

## First success target

```text
macOS boots
→ H1mekaRTXProbe loads
→ PCI match hits 10de:2f04
→ logs vendor/device/class/revision/subsystem
→ logs BAR region metadata
→ IORegistry shows H1mekaRTXProbe attached
```

## Do not implement yet

- No MMIO writes
- No VRAM writes
- No GSP initialization
- No display engine writes
- No Metal registration

## Required macOS-side tools

- macOS with Xcode
- Apple Developer account
- DriverKit entitlement path
- PCIDriverKit framework
- IORegistryExplorer or `ioreg`
- `log stream` for runtime logs
