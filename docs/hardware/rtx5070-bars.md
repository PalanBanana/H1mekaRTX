# RTX 5070 BAR Layout

## Observed BARs

| BAR | Address range | Size | Notes |
|---|---:|---:|---|
| BAR0 | 0x74000000-0x77ffffff | 64 MiB | likely MMIO register aperture |
| BAR1 | 0x4400000000-0x47ffffffff | 16 GiB | likely VRAM aperture / Resizable BAR |
| BAR3 | 0x4810000000-0x4811ffffff | 32 MiB | additional control/MMIO region |
| BAR5 | 0x4000-0x407f | 128 B | I/O port region |
| ROM | 0x78000000-0x7807ffff | 512 KiB | expansion ROM window |

## Stage 1 Policy

Read-only only.

Allowed:
- enumerate BARs
- log BAR index, size, and flags
- map BAR0 read-only if DriverKit allows it

Forbidden:
- MMIO writes
- VRAM writes
- firmware upload
- display engine programming
