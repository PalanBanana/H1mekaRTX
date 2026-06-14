# Actual Local Activation Hard Opt-In Check

- Decision: `PASS_ACTUAL_LOCAL_ACTIVATION_HARD_OPTIN_READY`
- Default Refuses Activation: `True`
- Hard Opt-In Flags Required: `True`
- CI Activation Attempted: `False`
- Activation Submitted By Default: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/actual-local-activation-hard-optin.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/actual-local-activation-hard-optin.md |
| `script_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/scripts/actual-local-activation-hard-optin.py |
| `phase56_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/manual-activation-preflight-after-signed-verification.json |
| `phase46_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/user-approved-system-extension-activation-path.json |
| `manifest_schema` | PASS |  |
| `default_refuses_activation_true` | PASS |  |
| `hard_optin_flags_required_true` | PASS |  |
| `ci_activation_attempted_false` | PASS |  |
| `activation_submitted_by_default_false` | PASS |  |
| `script_requires_understand_flag` | PASS |  |
| `script_requires_submit_activation_flag` | PASS |  |
| `script_requires_signing_identity` | PASS |  |
| `script_requires_output_under_host_report_bundle` | PASS |  |
| `script_checks_activation_preflight_ready` | PASS |  |
| `script_builds_swift_host` | PASS |  |
| `script_uses_activation_capable_host` | PASS |  |
| `script_captures_systemextensionsctl` | PASS |  |
| `script_keeps_provider_open_blocked` | PASS |  |
| `script_keeps_bar_mapping_blocked` | PASS |  |
| `script_keeps_gpu_command_blocked` | PASS |  |
