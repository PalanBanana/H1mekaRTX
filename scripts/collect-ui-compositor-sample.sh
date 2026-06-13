#!/usr/bin/env bash
set -u

OUT="${1:-$HOME/Desktop/H1mekaRTX-ui-compositor-sample-$(date +%Y%m%d-%H%M%S)}"
LABEL="${H1MEKARTX_UI_SAMPLE_LABEL:-manual-ui-sample}"
LAST="${H1MEKARTX_UI_SAMPLE_LAST:-5m}"

mkdir -p "$OUT"

echo "== H1mekaRTX UI compositor sample diagnostics =="
echo "Output: $OUT"
echo "Label:  $LABEL"
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

cat > "$OUT/sample-metadata.json" <<EOF
{
  "schema": "h1mekartx.ui_compositor_sample_metadata.v1",
  "label": "$LABEL",
  "logWindow": "$LAST",
  "classification": {
    "graphicsStackDiagnostics": true,
    "uiCompositorProof": false,
    "metalProof": false
  }
}
EOF

run_capture sw_vers.txt sw_vers
run_capture uptime.txt uptime
run_capture system_profiler-SPDisplaysDataType.txt system_profiler SPDisplaysDataType
run_capture system_profiler-SPDisplaysDataType.json system_profiler SPDisplaysDataType -json
run_capture ioreg-IODisplayConnect.txt ioreg -l -r -c IODisplayConnect
run_capture ioreg-IOFramebuffer.txt ioreg -l -r -c IOFramebuffer
run_capture ioreg-IOAccelerator.txt ioreg -l -r -c IOAccelerator

run_shell_capture process-windowserver-dock.txt \
  'ps -axo pid,ppid,stat,comm,args | grep -Ei "WindowServer|Dock|loginwindow|ControlCenter" | grep -v grep'

run_shell_capture ui-preferences.txt \
  'defaults read NSGlobalDomain AppleReduceTransparency; defaults read NSGlobalDomain AppleReduceMotion; defaults read com.apple.dock magnification; defaults read com.apple.dock autohide; defaults read com.apple.dock expose-animation-duration'

run_shell_capture ioreg-graphics-filtered.txt \
  'ioreg -l -p IOService | grep -iE "IODisplay|IOFramebuffer|IOGraphics|IOAccelerator|Metal|AGX|AppleCLCD|display|accelerator|GPU"'

run_shell_capture logs-ui-compositor-window.txt \
  "log show --last '$LAST' --style compact --predicate '(process == \"WindowServer\") OR (process == \"Dock\") OR (eventMessage CONTAINS[c] \"CoreAnimation\") OR (eventMessage CONTAINS[c] \"QuartzCore\") OR (eventMessage CONTAINS[c] \"Metal\") OR (eventMessage CONTAINS[c] \"IOAccelerator\") OR (eventMessage CONTAINS[c] \"IODisplay\") OR (eventMessage CONTAINS[c] \"IOFramebuffer\") OR (eventMessage CONTAINS[c] \"backdrop\") OR (eventMessage CONTAINS[c] \"blur\") OR (eventMessage CONTAINS[c] \"vibrancy\")'"

cat > "$OUT/README.txt" <<EOF
H1mekaRTX UI compositor sample diagnostics

Label: $LABEL
Log window: $LAST

Suggested manual sequence before running:
- Move a window.
- Resize a window.
- Open Mission Control.
- Open Launchpad.
- Move the pointer over Dock icons if Dock magnification is enabled.
- Observe transparency, blur, menu bar, Dock, sidebars, and Notification Center.

Classification:
- Graphics stack diagnostics: collected.
- UI compositor proof: unproven.
- Metal proof: unproven.

Safety boundary:
No DriverKit activation.
No System Extension activation.
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
