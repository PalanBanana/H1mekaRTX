# Sanitized Provider Visibility Evidence Matrix

- Decision: `PASS_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_MATRIX_READY`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Evidence Matrix Only: `True`
- Input Summary Present: `True`
- Input Check Present: `True`
- PASS Count: `9`
- BLOCKED Count: `2`
- MISSING Count: `0`
- NOT_PROVEN Count: `5`
- FAIL Count: `0`
- Provider Visibility Commands Executed By This Phase: `False`
- Raw Capture Parsed By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase62k-local-optin-provider-visibility-evidence-capture-runbook`

## Matrix

| Evidence ID | Status | Evidence |
| --- | --- | --- |
| `rtx5070_target_identity` | `PASS` | `{"expected_device_id": "0x2f04", "expected_iopcimatch": "0x2f0410de", "expected_vendor_id": "0x10de"}` |
| `sanitized_parser_summary_present` | `PASS` | `{"summary_present": true}` |
| `sanitized_parser_check_present` | `PASS` | `{"check_decision": "PASS_SANITIZED_LOCAL_PROVIDER_VISIBILITY_CAPTURE_PARSER_READY", "check_present": true}` |
| `raw_capture_availability` | `PASS` | `{"raw_capture_exists_local": true}` |
| `hard_opt_in_state` | `BLOCKED` | `{"hard_opt_in_matched": false}` |
| `raw_capture_read_state` | `BLOCKED` | `{"raw_capture_read": false}` |
| `provider_visibility_h1mekartx_token` | `NOT_PROVEN` | `{"detected_any_h1mekartx": false}` |
| `provider_visibility_iopcidevice_token` | `NOT_PROVEN` | `{"detected_any_iopcidevice": false}` |
| `provider_visibility_pci_identity_tokens` | `NOT_PROVEN` | `{"detected_any_10de": false, "detected_any_2f04": false, "detected_any_2f0410de": false}` |
| `provider_open_safety` | `PASS` | `{"provider_open_attempted": false}` |
| `ioserviceopen_safety` | `PASS` | `{"ioserviceopen_attempted": false}` |
| `bar_mapping_safety` | `PASS` | `{"bar_mapping_attempted": false}` |
| `bar0_read_write_safety` | `PASS` | `{"bar0_read_attempted": false, "bar0_write_attempted": false}` |
| `gpu_command_safety` | `PASS` | `{"gpu_command_submission_attempted": false}` |
| `metal_proof_state` | `NOT_PROVEN` | `{"current_rtx5070_metal_acceleration_claimed": false}` |
| `dock_transparency_blur_proof_state` | `NOT_PROVEN` | `{"dock_transparency_blur_acceleration_claimed": false}` |
