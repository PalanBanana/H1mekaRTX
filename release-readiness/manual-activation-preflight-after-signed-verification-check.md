# Manual Activation Preflight After Signed Verification Check

- Decision: `PASS_ACTIVATION_PREFLIGHT_BLOCKED_UNTIL_SIGNED_VERIFICATION`
- Preflight Gate Only: `True`
- Activation Preflight Ready: `False`
- Activation Allowed Now: `False`
- Deactivation Allowed Now: `False`
- Signed Artifact Verification OK: `False`
- Signed Package Created Locally: `False`
- Hard Opt-In OK: `False`
- Local Scope OK: `True`
- User Approval Allowed For Future Local Test: `True`
- Phase 46 Activation Path Exists: `True`
- Boundary OK: `True`
- Install Attempted: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Activation Block Reasons

| Reason |
| --- |
| `signed_artifact_verification_ok_false_or_missing` |
| `signed_package_created_locally_false_or_missing` |
| `hard_optin_ok_false_or_missing` |

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/manual-activation-preflight-after-signed-verification.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/manual-activation-preflight-after-signed-verification.md |
| `signed_summary_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/signed-artifact-verification-report-summary.json |
| `phase55_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/signed-artifact-verification-report-sanitizer.json |
| `phase54_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/actual-local-signing-hard-optin.json |
| `phase47_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/manual-activation-approval-readiness-gate.json |
| `phase46_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/user-approved-system-extension-activation-path.json |
| `manifest_schema` | PASS | manifest schema |
| `phase55_schema` | PASS | phase55 schema |
| `phase54_schema` | PASS | phase54 schema |
| `phase47_user_approval_allowed` | PASS | manual approval allowed |
| `phase46_activation_path_exists` | PASS | activation capable code |
| `signed_summary_schema` | PASS | signed summary schema |
| `boundary_activation_still_blocked` | PASS | activation still blocked |
| `boundary_provider_open_still_blocked` | PASS | provider open still blocked |
| `boundary_bar_mapping_still_blocked` | PASS | bar mapping still blocked |
| `boundary_gpu_command_submission_still_blocked` | PASS | gpu command still blocked |
| `manifest_manual_activation_preflight_gate_ready_true` | PASS | manual_activation_preflight_gate_ready |
| `manifest_preflight_gate_only_true` | PASS | preflight_gate_only |
| `manifest_activation_allowed_now_false` | PASS | activation_allowed_now |
| `manifest_deactivation_allowed_now_false` | PASS | deactivation_allowed_now |
| `manifest_install_attempted_false` | PASS | install_attempted |
| `manifest_system_extension_activation_attempted_false` | PASS | system_extension_activation_attempted |
| `manifest_system_extension_deactivation_attempted_false` | PASS | system_extension_deactivation_attempted |
| `manifest_dext_load_attempted_false` | PASS | dext_load_attempted |
| `manifest_provider_open_attempted_false` | PASS | provider_open_attempted |
| `manifest_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `manifest_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `manifest_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `manifest_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `manifest_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `manifest_metal_proof_claimed_false` | PASS | metal_proof_claimed |
