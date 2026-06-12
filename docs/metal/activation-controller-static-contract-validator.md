# Activation-controller Static Contract Validator

## Purpose

Stage 47 adds an activation-controller static contract validator.

The validator checks that the Stage 46 activation-controller design stub remains design-only and contains no activation runtime path.

This is not System Extension activation.

This is not activation request creation.

This is not manager submit.

This is not DriverKit target creation.

This is not DriverKit activation.

This is not provider attach.

This is not device ownership.

This is not PCI, BAR, or MMIO access.

This is not RTX 5070 Metal acceleration implementation.

## Decision

Current expected decision:

    PASS_ACTIVATION_CONTROLLER_STATIC_CONTRACT_VALIDATOR_READY

## Usage

Generate the design stub first:

    ./scripts/generate-activation-controller-design-stub.py --out-dir .

Then validate the static contract:

    ./scripts/validate-activation-controller-static-contract.py --root . --input-dir . --out-dir .

Check with local fixtures:

    ./scripts/check-activation-controller-static-contract.py --root . --out-dir .

## Validation Coverage

The validator checks:

- activation-controller design stub JSON exists
- activation-controller design stub decision is no-runtime
- exact RTX 5070 target identity
- activation-controller runtime remains blocked
- activation request remains blocked
- deactivation request remains blocked
- manager submit remains blocked
- DriverKit target creation remains blocked
- provider attach remains blocked
- device ownership remains blocked
- hardware access remains blocked
- runtime state remains blocked
- provider state remains blocked
- hardware state remains blocked
- source files contain no forbidden activation, DriverKit, PCI, BAR, MMIO, or RTX 5070 acceleration implementation tokens

## Safety Boundary

This stage is local JSON validation and static source scanning only.

It does not create activation request objects, create deactivation request objects, call extension manager submit, implement an activation controller runtime path, create DriverKit targets, add dext provider classes, add Info.plist provider-match dictionaries, activate DriverKit, install DriverKit dexts, request device ownership, attach to PCI providers, query live provider state, query live extension status, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.

## Next Stage

Stage 48 should add an activation-controller transition gate report. It should continue to report NO-GO until provider-match transition, entitlement evidence, bundle identity evidence, rollback evidence, and safety gates are all complete.
