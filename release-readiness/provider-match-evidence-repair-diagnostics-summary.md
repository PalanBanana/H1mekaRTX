# Provider Match Evidence Repair Diagnostics Summary

- Generated At UTC: `2026-06-14T03:22:13.199282+00:00`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Read-Only Diagnostics Only: `True`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
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
| `codesign_display_dext` | `True` | `0` | `False` | `True` |
| `codesign_display_host` | `True` | `0` | `False` | `True` |
| `ioreg_h1meka_filtered` | `True` | `0` | `True` | `False` |
| `ioreg_iopcidevice` | `True` | `0` | `True` | `False` |
| `system_profiler_displays` | `True` | `0` | `True` | `False` |
| `systemextensionsctl_list` | `True` | `0` | `True` | `False` |

## Derived Evidence

| Key | Value |
| --- | --- |
| `host_bundle_exists` | `True` |
| `dext_bundle_exists` | `True` |
| `host_info_parse_ok` | `True` |
| `dext_info_parse_ok` | `True` |
| `host_bundle_id_matches` | `True` |
| `dext_bundle_id_matches` | `True` |
| `dext_personalities_present` | `True` |
| `dext_personality_provider_class_matches` | `True` |
| `dext_personality_iopcimatch_matches` | `True` |
| `systemextensionsctl_available` | `True` |
| `systemextensionsctl_returncode` | `0` |
| `extension_identifier_observed_in_systemextensionsctl` | `False` |
| `systemextension_status_tokens` | `[]` |
| `ioreg_available` | `True` |
| `ioreg_iopcidevice_returncode` | `0` |
| `rtx_vendor_10de_observed_in_ioreg` | `True` |
| `rtx_device_2f04_observed_in_ioreg` | `True` |
| `rtx_iopcimatch_2f0410de_observed_in_ioreg` | `False` |
| `extension_identifier_observed_in_ioreg` | `False` |
| `h1meka_string_observed_in_ioreg` | `False` |
| `nvidia_string_observed_in_ioreg` | `False` |
| `display_profiler_nvidia_observed` | `True` |
| `display_profiler_rtx_observed` | `False` |
| `provider_match_blocked_reason_hint` | `['extension_identifier_not_observed_in_systemextensionsctl']` |
| `provider_open_still_blocked` | `True` |
| `ioserviceopen_still_blocked` | `True` |
| `bar_mapping_still_blocked` | `True` |
| `gpu_command_submission_still_blocked` | `True` |
| `dock_transparency_blur_proof_still_blocked` | `True` |

## Repair Decision

| Key | Value |
| --- | --- |
| `extension_status_observed` | `False` |
| `pci_identity_observed` | `True` |
| `personality_matches` | `True` |
| `bundle_ids_match` | `True` |
| `provider_open_allowed` | `False` |
| `repaired_provider_match_ready` | `False` |
| `next_gate_if_ready` | `rerun provider-match-without-open readiness gate` |
| `next_gate_if_blocked` | `fix system extension activation/provider personality/PCI identity evidence` |
