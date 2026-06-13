#!/usr/bin/env bash
set -u

OUT="${1:-$HOME/Desktop/H1mekaRTX-host-diagnostics-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$OUT"

echo "== H1mekaRTX host + UI compositor diagnostics =="
echo "Output: $OUT"

run_capture() {
  local name="$1"
  shift

  {
    echo "\$ $*"
    "$@"
    status="$?"
    echo
    echo "exit_status=$status"
  } > "$OUT/$name" 2>&1
}

run_shell_capture() {
  local name="$1"
  shift

  {
    echo "\$ $*"
    /bin/sh -c "$*"
    status="$?"
    echo
    echo "exit_status=$status"
  } > "$OUT/$name" 2>&1
}

run_capture sw_vers.txt sw_vers
run_capture uname.txt uname -a
run_capture arch.txt arch
run_capture csrutil-status.txt csrutil status

run_capture system_profiler-SPHardwareDataType.txt system_profiler SPHardwareDataType
run_capture system_profiler-SPPCIDataType.txt system_profiler SPPCIDataType
run_capture system_profiler-SPDisplaysDataType.txt system_profiler SPDisplaysDataType
run_capture system_profiler-SPDisplaysDataType.json system_profiler SPDisplaysDataType -json

run_capture ioreg-IODeviceTree.txt ioreg -l -p IODeviceTree
run_capture ioreg-IOService.txt ioreg -l -p IOService
run_capture ioreg-IOPCIDevice.txt ioreg -l -r -c IOPCIDevice
run_capture ioreg-IODisplayConnect.txt ioreg -l -r -c IODisplayConnect
run_capture ioreg-IOFramebuffer.txt ioreg -l -r -c IOFramebuffer
run_capture ioreg-IOAccelerator.txt ioreg -l -r -c IOAccelerator

run_shell_capture ioreg-rtx5070-filtered.txt \
  'ioreg -l -p IOService | grep -iE "10de|2f04|IOPCIMatch|assigned-addresses|reg|AAPL,slot-name|class-code|device-id|vendor-id|subsystem|IOPCIDevice|IOName|IOProviderClass"'

run_shell_capture ioreg-graphics-filtered.txt \
  'ioreg -l -p IOService | grep -iE "IODisplay|IOFramebuffer|IOGraphics|IOAccelerator|Metal|AGX|AppleCLCD|WindowServer|CoreAnimation|QuartzCore|display|accelerator|GPU"'

run_shell_capture process-windowserver-dock.txt \
  'ps -axo pid,ppid,stat,comm,args | grep -Ei "WindowServer|Dock|loginwindow|ControlCenter" | grep -v grep'

run_shell_capture frameworks-graphics.txt \
  'for p in /System/Library/Frameworks/Metal.framework /System/Library/Frameworks/QuartzCore.framework /System/Library/Frameworks/CoreGraphics.framework /System/Library/Frameworks/IOSurface.framework /System/Library/PrivateFrameworks/SkyLight.framework; do ls -ld "$p"; done'

run_shell_capture ui-preferences.txt \
  'defaults read NSGlobalDomain AppleReduceTransparency; defaults read NSGlobalDomain AppleReduceMotion; defaults read com.apple.dock magnification; defaults read com.apple.dock autohide'

run_shell_capture logs-graphics-ui-last30m.txt \
  'log show --last 30m --style compact --predicate "(process == \"WindowServer\") OR (process == \"Dock\") OR (eventMessage CONTAINS[c] \"CoreAnimation\") OR (eventMessage CONTAINS[c] \"QuartzCore\") OR (eventMessage CONTAINS[c] \"Metal\") OR (eventMessage CONTAINS[c] \"IOAccelerator\") OR (eventMessage CONTAINS[c] \"IODisplay\") OR (eventMessage CONTAINS[c] \"IOFramebuffer\") OR (eventMessage CONTAINS[c] \"H1mekaRTX\")"'

cat > "$OUT/README.txt" <<'EOF'
H1mekaRTX host + UI compositor diagnostics

Classification:
- Host diagnostics: PCIe identity, BAR-like OS inventory, IORegistry visibility, host OS state.
- Graphics stack diagnostics: IODisplay, IOFramebuffer, IOGraphics, IOAccelerator, Metal, WindowServer, Dock, Core Animation, QuartzCore hints.

This collection is read-only.

No DriverKit activation.
No System Extension activation.
No device ownership request.
No PCI config-space writes.
No MMIO writes.
No BAR mapping.
No BAR poking.
No GPU reset.
No firmware loading.
No GSP initialization.
No display engine initialization.
No framebuffer initialization.
No GPU command submission.
No RTX 5070 shader execution.
No RTX 5070 Metal acceleration claim.
No RTX 5070 UI compositor acceleration claim.
EOF

echo "$OUT"
