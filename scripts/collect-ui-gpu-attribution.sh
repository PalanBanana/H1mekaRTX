#!/usr/bin/env bash
set -u

OUT="${1:-$HOME/Desktop/H1mekaRTX-ui-gpu-attribution-$(date +%Y%m%d-%H%M%S)}"
LAST="${H1MEKARTX_UI_ATTRIBUTION_LAST:-10m}"

mkdir -p "$OUT"

echo "== H1mekaRTX UI GPU attribution diagnostics =="
echo "Output: $OUT"
echo "Last:   $LAST"

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

cat > "$OUT/attribution-metadata.json" <<EOF
{
  "schema": "h1mekartx.ui_gpu_attribution_metadata.v1",
  "logWindow": "$LAST",
  "classification": {
    "graphicsStackDiagnostics": true,
    "trustedUiGpuAttribution": false,
    "uiCompositorProof": false,
    "metalProof": false
  }
}
EOF

run_capture sw_vers.txt sw_vers
run_capture system_profiler-SPDisplaysDataType.txt system_profiler SPDisplaysDataType
run_capture system_profiler-SPDisplaysDataType.json system_profiler SPDisplaysDataType -json
run_capture ioreg-IOFramebuffer.txt ioreg -l -r -c IOFramebuffer
run_capture ioreg-IOAccelerator.txt ioreg -l -r -c IOAccelerator
run_capture ioreg-IODisplayConnect.txt ioreg -l -r -c IODisplayConnect

run_shell_capture process-windowserver-dock.txt \
  'ps -axo pid,ppid,stat,comm,args | grep -Ei "WindowServer|Dock|loginwindow|ControlCenter" | grep -v grep'

run_shell_capture ioreg-display-accelerator-filtered.txt \
  'ioreg -l -p IOService | grep -iE "IOFramebuffer|IOAccelerator|IODisplay|IODisplayConnect|AppleCLCD|AGX|Metal|display|accelerator|gpu|vendor-id|device-id|IOPCIMatch|IOProviderClass|IOName|AAPL,slot-name"'

run_shell_capture logs-ui-gpu-attribution.txt \
  "log show --last '$LAST' --style compact --predicate '(process == \"WindowServer\") OR (process == \"Dock\") OR (eventMessage CONTAINS[c] \"IOAccelerator\") OR (eventMessage CONTAINS[c] \"IOFramebuffer\") OR (eventMessage CONTAINS[c] \"IODisplay\") OR (eventMessage CONTAINS[c] \"Metal\") OR (eventMessage CONTAINS[c] \"GPU\") OR (eventMessage CONTAINS[c] \"display\")'"

cat > "$OUT/README.txt" <<EOF
H1mekaRTX UI GPU attribution diagnostics

Log window: $LAST

Purpose:
- Collect read-only candidate evidence for which GPU/display/accelerator paths macOS exposes around WindowServer and Dock.

Classification:
- Graphics stack diagnostics: collected.
- Trusted UI GPU attribution: not proven.
- UI compositor proof: unproven.
- Metal proof: unproven.

Safety boundary:
No DriverKit activation.
No System Extension activation.
No device ownership request.
No process injection.
No WindowServer injection.
No Dock injection.
No private framework patching.
No SIP/AMFI bypass.
No PCI config-space writes.
No MMIO reads.
No MMIO writes.
No BAR mapping.
No GPU command submission.
No RTX 5070 UI compositor acceleration claim.
No RTX 5070 Metal acceleration claim.
EOF

echo "$OUT"
