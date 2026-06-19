# Local-Only Final Review Command Checklist

Phase 63K adds a local-only final review command checklist for the redacted entitlement request packet.

This phase is local-final-review-command-checklist-only.

This phase only records commands that a human can run locally to review redacted artifacts.

This phase does not execute the checklist commands.

This phase does not create an export archive.

This phase does not copy files into an export bundle.

This phase does not export provisioning assets.

This phase does not export certificates.

This phase does not export private keys.

This phase does not export raw IORegistry data.

This phase does not export provider handles.

This phase does not submit an Apple entitlement request.

This phase does not contact Apple.

This phase does not create an App ID.

This phase does not create a provisioning profile.

This phase does not sign a DriverKit extension.

This phase does not load or activate a DriverKit extension.

This phase does not open a provider.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not read BAR0.

This phase does not write BAR0.

This phase does not mutate BAR/MMIO.

This phase does not submit GPU commands.

This phase does not claim RTX 5070 Metal acceleration.

This phase does not claim Dock/transparency/blur acceleration.

## Checklist Command Policy

Allowed command classes:

- `git status`, `git log`, and `git diff --name-only`
- `gh pr view` and `gh run list` read-only inspection
- `python3 -m json.tool` for local JSON formatting
- `grep` for local release-readiness assertions
- `sed -n` for local document preview

Forbidden command classes:

- Apple request submission
- Apple contact or web form automation
- archive creation
- file copy into a bundle
- certificate export
- private key export
- provisioning profile export
- raw IORegistry export
- provider handle export
- provider open
- IOServiceOpen
- BAR/MMIO access
- BAR0 read/write
- PCI config write
- firmware loading
- GPU reset
- framebuffer/display engine init
- GPU command submission
- Metal acceleration proof claim
- Dock/transparency/blur acceleration claim

## Next Gate

Phase 63L should add a local-only final review checklist consistency gate.

Phase 63L must still not submit the entitlement request, contact Apple, create an archive, copy files, export secrets, open a provider, touch BAR/MMIO, submit GPU commands, or claim Metal/Dock acceleration.
