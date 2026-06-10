#!/usr/bin/env bash
set -euo pipefail

echo "IORegistry NVIDIA search:"
ioreg -l | grep -Ei "10de|2f04|H1mekaRTX|NVIDIA" || true

echo
echo "Live logs containing H1mekaRTX:"
log stream --style compact --predicate 'eventMessage CONTAINS "H1mekaRTX" OR process CONTAINS "H1mekaRTX"'
