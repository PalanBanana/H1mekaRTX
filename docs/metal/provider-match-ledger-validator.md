# Provider-match Ledger Validator

## Purpose

Stage 44 adds a provider-match ledger validator.

The validator consumes local generated JSON reports and cross-checks:

- provider-match-evidence-ledger.json
- provider-match-dry-run-spec.json
- entitlement-evidence-checklist.json
- no-hardware-activation-readiness-review.json

This is not DriverKit target creation.

This is not System Extension activation.

This is not DriverKit activation.

This is not provider attach.

This is not device ownership.

This is not PCI, BAR, or MMIO access.

This is not RTX 5070 Metal acceleration implementation.

## Decision

Current decision:

    PASS_PROVIDER_MATCH_LEDGER_VALIDATOR_READY

## Usage

Generate the required local JSON reports first:

    ./scripts/generate-provider-match-dry-run-spec.py --out-dir .
    ./scripts/generate-entitlement-evidence-checklist.py --out-dir .
    ./scripts/generate-no-hardware-activation-readiness-review.py --out-dir .
    ./scripts/generate-provider-match-evidence-ledger.py --out-dir .

Then validate:

    ./scripts/validate-provider-match-evidence-ledger.py --input-dir . --out-dir .

Check with local fixtures:

    ./scripts/check-provider-match-ledger-validator.py --root . --out-dir .

## Validation Coverage

The validator checks:

- expected report decisions
- exact RTX 5070 target identity
- provider-match transition remains blocked
- DriverKit target creation remains blocked
- activation request remains blocked
- provider attach remains blocked
- device ownership remains blocked
- hardware access remains blocked
- dry-run spec has zero failed cases
- entitlement checklist still requires user evidence
- readiness review still requires evidence
- source artifacts are linked by the ledger
- safety boundaries remain false for activation, DriverKit, PCI, BAR, MMIO, and RTX 5070 acceleration paths

## Safety Boundary

This stage is local JSON validation only.

It does not create DriverKit targets, add dext provider classes, add Info.plist provider-match dictionaries, create activation request objects, create deactivation request objects, call extension manager submit, implement an activation controller runtime path, activate DriverKit, install DriverKit dexts, request device ownership, attach to PCI providers, query live provider state, query live extension status, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.

## Next Stage

Stage 45 should add a provider-match transition gate report that summarizes whether provider work can advance. Current expectation remains NO-GO until private entitlement and bundle identity evidence exists outside the repository.
