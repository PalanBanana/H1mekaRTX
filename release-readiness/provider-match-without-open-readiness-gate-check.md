# Provider Match Without Open Readiness Gate Check

- Decision: `PASS_PROVIDER_MATCH_WITHOUT_OPEN_BLOCKED_PENDING_EVIDENCE`
- Provider Match Without Open Ready: `False`
- Provider Open Allowed Now: `False`
- IOServiceOpen Allowed Now: `False`
- BAR Mapping Allowed Now: `False`
- GPU Command Submission Allowed Now: `False`
- Activation Command Completed: `True`
- Extension Identifier Observed In Systemextensionsctl: `False`
- RTX Vendor 0x10de Observed: `True`
- RTX Device 0x2f04 Observed: `True`
- RTX IOPCIMatch 0x2f0410de Observed: `False`
- Provider Open Still Blocked: `True`
- IOServiceOpen Still Blocked: `True`
- BAR Mapping Still Blocked: `True`
- GPU Command Submission Still Blocked: `True`

## Block Reasons

| Reason |
| --- |
| `extension_identifier_not_observed_in_systemextensionsctl` |

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/provider-match-without-open-readiness-gate.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/provider-match-without-open-readiness-gate.md |
| `phase59_summary_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/dext-load-provider-match-status-summary.json |
| `phase59_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/dext-load-provider-match-status-evidence.json |
| `manifest_schema` | PASS | manifest schema |
| `phase59_summary_schema` | PASS | phase59 summary schema |
| `phase59_manifest_schema` | PASS | phase59 manifest schema |
| `manifest_provider_match_without_open_readiness_gate_ready_true` | PASS | provider_match_without_open_readiness_gate_ready |
| `manifest_preflight_gate_only_true` | PASS | preflight_gate_only |
| `manifest_provider_open_allowed_now_false` | PASS | provider_open_allowed_now |
| `manifest_ioserviceopen_allowed_now_false` | PASS | ioserviceopen_allowed_now |
| `manifest_bar_mapping_allowed_now_false` | PASS | bar_mapping_allowed_now |
| `manifest_gpu_command_submission_allowed_now_false` | PASS | gpu_command_submission_allowed_now |
| `manifest_activation_submitted_by_this_phase_false` | PASS | activation_submitted_by_this_phase |
| `manifest_deactivation_submitted_by_this_phase_false` | PASS | deactivation_submitted_by_this_phase |
| `manifest_install_attempted_false` | PASS | install_attempted |
| `manifest_manual_dext_load_attempted_false` | PASS | manual_dext_load_attempted |
| `manifest_provider_open_attempted_false` | PASS | provider_open_attempted |
| `manifest_ioserviceopen_attempted_false` | PASS | ioserviceopen_attempted |
| `manifest_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `manifest_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `manifest_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `manifest_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `manifest_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `manifest_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `phase59_readiness_provider_open_allowed_false` | PASS | provider open allowed false |
| `phase59_derived_provider_open_still_blocked` | PASS | provider open blocked |
| `phase59_derived_ioserviceopen_still_blocked` | PASS | IOServiceOpen blocked |
| `phase59_derived_bar_mapping_still_blocked` | PASS | BAR mapping blocked |
| `phase59_derived_gpu_command_submission_still_blocked` | PASS | GPU command blocked |
