#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-$HOME/Desktop/H1mekaRTX-sysext-diagnostics-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$OUT"

sw_vers > "$OUT/sw_vers.txt" 2>&1 || true
uname -a > "$OUT/uname.txt" 2>&1 || true
xcodebuild -version > "$OUT/xcodebuild-version.txt" 2>&1 || true

systemextensionsctl list > "$OUT/systemextensionsctl-list.txt" 2>&1 || true

system_profiler SPPCIDataType > "$OUT/system_profiler-SPPCIDataType.txt" 2>&1 || true

ioreg -l -p IODeviceTree > "$OUT/ioreg-IODeviceTree.txt" 2>&1 || true
ioreg -l -p IOService > "$OUT/ioreg-IOService.txt" 2>&1 || true

log show --last 30m --style compact \
  --predicate '(process == "sysextd") OR (eventMessage CONTAINS[c] "H1mekaRTX") OR (eventMessage CONTAINS[c] "DriverKit") OR (eventMessage CONTAINS[c] "SystemExtension")' \
  > "$OUT/log-show-sysext-driverkit-last30m.txt" 2>&1 || true

printf '%s\n' "$OUT"
