#!/usr/bin/env bash
set -u

OUT="${1:-$HOME/Desktop/H1mekaRTX-bar-inventory-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$OUT"

echo "== H1mekaRTX BAR inventory diagnostics =="
echo "Output: $OUT"

sw_vers > "$OUT/sw_vers.txt" 2>&1
uname -a > "$OUT/uname.txt" 2>&1
system_profiler SPPCIDataType > "$OUT/system_profiler-SPPCIDataType.txt" 2>&1
system_profiler SPDisplaysDataType > "$OUT/system_profiler-SPDisplaysDataType.txt" 2>&1

ioreg -l -p IODeviceTree > "$OUT/ioreg-IODeviceTree.txt" 2>&1
ioreg -l -p IOService > "$OUT/ioreg-IOService.txt" 2>&1

ioreg -l -p IOService | grep -iE "10de|2f04|IOPCIMatch|assigned-addresses|reg|AAPL,slot-name|class-code|device-id|vendor-id|subsystem" > "$OUT/ioreg-rtx5070-filtered.txt" 2>&1

log show --last 30m --style compact --predicate '(eventMessage CONTAINS[c] "H1mekaRTX") OR (eventMessage CONTAINS[c] "IOPCIDevice") OR (eventMessage CONTAINS[c] "DriverKit") OR (eventMessage CONTAINS[c] "sysextd")' > "$OUT/logs-driverkit-pci-last30m.txt" 2>&1

cat > "$OUT/README.txt" <<EOF
H1mekaRTX BAR inventory diagnostics

This collection is read-only.

No MMIO writes.
No BAR poking.
No GPU reset.
No firmware loading.
No display engine initialization.
No framebuffer initialization.
No Metal acceleration attempt.
EOF

echo "$OUT"
