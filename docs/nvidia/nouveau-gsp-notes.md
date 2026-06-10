# Nouveau / GSP Notes

The Linux dump shows the GPU binding to `nouveau` and includes GSP-related initialization logs.

Useful observed lines include:

```text
NVIDIA GB205
GSP RM version: 570.144
VRAM: 12227 MiB
MM: using COPY for buffer copies
nouveaudrmfb fb0
```

## Stage 2 direction

- Study Nouveau behavior around GB205 / Blackwell.
- Track GSP firmware initialization and RM version assumptions.
- Identify memory object/channel/fence/copy-engine concepts before attempting compute-only execution.
