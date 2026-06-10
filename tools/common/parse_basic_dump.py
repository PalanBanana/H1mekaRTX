#!/usr/bin/env python3
from pathlib import Path
import hashlib
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dumps/rtx5070-gigabyte-windforce-oc-12g")

def read_text(name: str) -> str:
    p = root / name
    if not p.exists():
        return "<missing>"
    return p.read_text(errors="replace").strip()

print("vendor:", read_text("vendor.txt"))
print("device:", read_text("device.txt"))
print("subsystem_vendor:", read_text("subsystem_vendor.txt"))
print("subsystem_device:", read_text("subsystem_device.txt"))
print("class:", read_text("class.txt"))
print("revision:", read_text("revision.txt"))

rom = root / "rtx5070-vbios.rom"
if rom.exists():
    data = rom.read_bytes()
    print("vbios_size:", len(data))
    print("vbios_sha256:", hashlib.sha256(data).hexdigest())
