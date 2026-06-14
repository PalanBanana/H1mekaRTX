# Activation Delegate Diagnostics Remediation Summary

- Generated At UTC: `2026-06-14T03:53:01.593479+00:00`
- Summary Only: `True`
- Local Delegate Report Present: `True`
- Local Delegate Decision: `PASS_DELEGATE_DIAGNOSTICS_CAPTURED_EXTENSION_NOT_VISIBLE`
- Activation Submitted Locally: `True`
- Extension Identifier Observed: `False`
- Delegate Did Finish: `False`
- Delegate Did Fail: `True`
- Delegate Needs User Approval: `False`
- Delegate Timeout: `False`
- Delegate Error Text Present: `True`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Sanitized Commands

| Command | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- |
| `build_delegate_diagnostics_host` | `0` | `False` | `True` |
| `log_show_sysext_kernelmanagerd` | `0` | `True` | `False` |
| `resign_embedded_dext` | `0` | `False` | `True` |
| `resign_host_app` | `0` | `False` | `False` |
| `submit_activation_with_delegate` | `4` | `True` | `False` |
| `systemextensionsctl_after` | `0` | `True` | `False` |
| `systemextensionsctl_before` | `0` | `True` | `False` |
| `verify_embedded_dext` | `0` | `False` | `True` |
| `verify_host_app` | `0` | `False` | `True` |

## Derived

| Key | Value |
| --- | --- |
| `build_delegate_diagnostics_host_ok` | `True` |
| `resign_embedded_dext_ok` | `True` |
| `verify_embedded_dext_ok` | `True` |
| `resign_host_app_ok` | `True` |
| `verify_host_app_ok` | `True` |
| `delegate_did_finish` | `False` |
| `delegate_did_fail` | `True` |
| `delegate_needs_user_approval` | `False` |
| `delegate_timeout` | `False` |
| `delegate_error_text_present` | `True` |
| `extension_visibility_observed_after_delegate` | `False` |
| `provider_open_still_blocked` | `True` |
| `ioserviceopen_still_blocked` | `True` |
| `bar_mapping_still_blocked` | `True` |
| `gpu_command_submission_still_blocked` | `True` |
| `dock_transparency_blur_proof_still_blocked` | `True` |

## Remediation

| Key | Value |
| --- | --- |
| `reason` | `delegate_did_fail` |
| `next_gate` | `phase60g_activation_error_remediation_plan` |
| `phase61_allowed_now` | `False` |
| `provider_open_allowed_now` | `False` |
| `bar_mapping_allowed_now` | `False` |
| `gpu_command_submission_allowed_now` | `False` |
