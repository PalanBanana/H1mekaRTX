# RTX 5070 BAR Layout

Source: `rtx5070-lspci-vvv.txt` and `resource.bin`.

| BAR | Address range | Size | Notes |
|---|---:|---:|---|
| BAR0 | `0x74000000` | 64 MiB | non-prefetchable MMIO |
| BAR1 | `0x4400000000` | 16 GiB | prefetchable, likely VRAM aperture / ReBAR |
| BAR3 | `0x4810000000` | 32 MiB | prefetchable auxiliary MMIO/window |
| BAR5 | `0x4000` | 128 B | I/O port region |
| Expansion ROM | `0x78000000` | 512 KiB window | ROM window disabled in lspci; dumped ROM is 162,304 bytes |

## PCIe link

- Capability: 32 GT/s x16
- Dumped current link state: 5 GT/s x16, downgraded at collection time
- Resizable BAR: BAR1 current size 16GB; supported 64MB through 16GB

## Stage 1 rule

Do not write to any mapped BAR region in `H1mekaRTXProbe`. Stage 1 is read-only probing only.
