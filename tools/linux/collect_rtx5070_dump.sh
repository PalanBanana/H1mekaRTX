#!/usr/bin/env bash
set -euo pipefail

GPU="${1:-01:00.0}"
GPU_FULL="0000:${GPU}"
DEV="/sys/bus/pci/devices/${GPU_FULL}"
OUT="${2:-H1mekaRTX-dump-fixed}"

mkdir -p "$OUT"
cd "$OUT"

sudo lspci -nnvvv -s "$GPU" > rtx5070-lspci-vvv.txt
sudo lspci -xxxx -s "$GPU" > rtx5070-pci-config-256b.txt
sudo lspci -xxxxxxx -s "$GPU" > rtx5070-pci-config-4096b.txt 2>/dev/null || true

for f in vendor device subsystem_vendor subsystem_device class revision resource irq config; do
  if [ -e "$DEV/$f" ]; then
    sudo cp "$DEV/$f" "./$f.bin" 2>/dev/null || sudo cat "$DEV/$f" > "./$f.txt" 2>/dev/null || true
  fi
done

sudo dmesg > dmesg-full.txt
sudo dmesg | grep -Ei "nvidia|nouveau|nova|gsp|gpu|drm|pci|01:00" > gpu-dmesg.txt || true
lsmod > lsmod.txt

echo 1 | sudo tee "$DEV/rom" >/dev/null 2>&1 || true
sudo cat "$DEV/rom" > rtx5070-vbios.rom 2>/dev/null || true
echo 0 | sudo tee "$DEV/rom" >/dev/null 2>&1 || true

sha256sum rtx5070-vbios.rom > rtx5070-vbios.sha256 2>/dev/null || true

echo "DONE: $(pwd)"
