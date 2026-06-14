# Local Activation Report + System Extension Status Summary

- Generated At UTC: `2026-06-14T03:07:53.713523+00:00`
- Sanitizer Only: `True`
- Host Report Bundle Local Only: `True`
- Local Activation Report Present: `True`
- Local Activation Decision: `PASS_LOCAL_ACTIVATION_COMMAND_COMPLETED`
- Hard Opt-In OK: `True`
- Local Scope OK: `True`
- Activation Preflight Ready: `True`
- Activation Submitted Locally: `True`
- Activation Command Return Code: `0`
- Activation Command Completed: `True`
- Systemextensionsctl Available: `True`
- Systemextensionsctl Return Code: `0`
- Extension Identifier Observed In Status: `False`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
- Activation Submitted By Sanitizer: `False`
- Deactivation Submitted By Sanitizer: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Dock Transparency Blur Proof Claimed: `False`

## System Extension Status Tokens

| Token |
| --- |
| `none` |

## Sanitized Command Summary

| Command | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- |
| `build_activation_capable_host` | `0` | `False` | `False` |
| `resign_embedded_dext` | `0` | `False` | `True` |
| `resign_host_app` | `0` | `False` | `False` |
| `submit_activation` | `0` | `True` | `False` |
| `systemextensionsctl_after` | `0` | `True` | `False` |
| `systemextensionsctl_before` | `0` | `True` | `False` |
| `verify_embedded_dext` | `0` | `False` | `True` |
| `verify_host_app` | `0` | `False` | `True` |

## Derived Runtime Boundary

| Key | Value |
| --- | --- |
| `build_activation_capable_host_ok` | `True` |
| `resign_embedded_dext_ok` | `True` |
| `verify_embedded_dext_ok` | `True` |
| `resign_host_app_ok` | `True` |
| `verify_host_app_ok` | `True` |
| `activation_request_was_submitted_by_host` | `True` |
| `provider_open_still_blocked` | `True` |
| `bar_mapping_still_blocked` | `True` |
| `gpu_command_submission_still_blocked` | `True` |
| `dock_transparency_blur_proof_still_blocked` | `True` |
