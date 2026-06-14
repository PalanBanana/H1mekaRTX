# Dext Load + Provider Match Status Summary

- Generated At UTC: `2026-06-14T03:10:42.613160+00:00`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Local Report Present: `True`
- Activation Submitted By This Phase: `False`
- Deactivation Submitted By This Phase: `False`
- Install Attempted: `False`
- Manual Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Sanitized Commands

| Command | Available | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- | --- |
| `ioreg_iopcidevice` | `True` | `0` | `True` | `False` |
| `ioreg_ioservice_h1meka` | `True` | `0` | `True` | `False` |
| `systemextensionsctl_list` | `True` | `0` | `True` | `False` |

## Derived Evidence

| Key | Value |
| --- | --- |
| `activation_report_present` | `True` |
| `activation_command_completed` | `True` |
| `activation_submitted_locally` | `True` |
| `systemextensionsctl_available` | `True` |
| `systemextensionsctl_returncode` | `0` |
| `extension_identifier_observed_in_systemextensionsctl` | `False` |
| `status_contains_activated` | `False` |
| `status_contains_enabled` | `False` |
| `status_contains_waiting_or_needs_user` | `False` |
| `ioreg_available` | `True` |
| `ioreg_iopcidevice_returncode` | `0` |
| `rtx_vendor_10de_observed` | `True` |
| `rtx_device_2f04_observed` | `True` |
| `rtx_iopcimatch_2f0410de_observed` | `False` |
| `extension_identifier_observed_in_ioreg` | `False` |
| `provider_open_still_blocked` | `True` |
| `ioserviceopen_still_blocked` | `True` |
| `bar_mapping_still_blocked` | `True` |
| `gpu_command_submission_still_blocked` | `True` |
| `dock_transparency_blur_proof_still_blocked` | `True` |

## Provider Match Readiness

| Key | Value |
| --- | --- |
| `system_extension_status_observed` | `False` |
| `rtx_pci_identity_observed` | `True` |
| `provider_open_allowed` | `False` |
| `next_gate` | `provider_match_without_open_readiness_gate` |
