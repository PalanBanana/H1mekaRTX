# Provider Match Repair Readiness Bridge Check

- Decision: `PASS_PROVIDER_MATCH_REPAIR_BLOCKED_PENDING_FIX`
- Provider Match Repair Bridge Ready: `False`
- Provider Open Allowed Now: `False`
- IOServiceOpen Allowed Now: `False`
- BAR Mapping Allowed Now: `False`
- GPU Command Submission Allowed Now: `False`
- Extension Status Observed: `False`
- PCI Identity Observed: `True`
- Personality Matches: `True`
- Bundle IDs Match: `True`
- Repaired Provider Match Ready: `False`
- Provider Open Still Blocked: `True`
- IOServiceOpen Still Blocked: `True`
- BAR Mapping Still Blocked: `True`
- GPU Command Submission Still Blocked: `True`
- Dock Transparency Blur Proof Still Blocked: `True`

## Block Reasons

| Reason |
| --- |
| `extension_status_observed_false` |
| `repaired_provider_match_ready_false` |

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/provider-match-repair-readiness-bridge.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/provider-match-repair-readiness-bridge.md |
| `phase60a_summary_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/provider-match-evidence-repair-diagnostics-summary.json |
| `phase60a_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/provider-match-evidence-repair-diagnostics.json |
| `phase60_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/provider-match-without-open-readiness-gate.json |
| `manifest_schema` | PASS | manifest schema |
| `phase60a_summary_schema` | PASS | phase60a summary schema |
| `phase60a_manifest_schema` | PASS | phase60a manifest schema |
| `phase60_manifest_schema` | PASS | phase60 manifest schema |
| `manifest_provider_match_repair_readiness_bridge_ready_true` | PASS | provider_match_repair_readiness_bridge_ready |
| `manifest_preflight_bridge_only_true` | PASS | preflight_bridge_only |
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
| `provider_open_still_blocked` | PASS | provider open boundary |
| `ioserviceopen_still_blocked` | PASS | IOServiceOpen boundary |
| `bar_mapping_still_blocked` | PASS | BAR mapping boundary |
| `gpu_command_submission_still_blocked` | PASS | GPU command boundary |
| `dock_transparency_blur_proof_still_blocked` | PASS | UI proof boundary |
