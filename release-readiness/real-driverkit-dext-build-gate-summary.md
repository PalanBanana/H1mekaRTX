# Real DriverKit Dext Build Gate Summary

- Generated At UTC: `2026-06-14T04:16:55.971740+00:00`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Real DriverKit Dext Built: `False`
- Phase 61 Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Details

| Key | Value |
| --- | --- |
| `local_build_report_present` | `True` |
| `local_build_decision` | `REFUSE_REAL_DRIVERKIT_BUILD_HARDOPTIN_OR_INPUT_NOT_SATISFIED` |
| `xcodebuild_attempted_locally` | `False` |
| `xcodebuild_build_ok` | `False` |
| `discovered_dext_count` | `None` |
| `matching_dext_count` | `None` |
| `selected_dext_present` | `False` |
| `selected_dext_identifier_matches` | `False` |
| `selected_dext_exec_present` | `False` |
| `selected_dext_codesign_ok` | `False` |
| `driverkit_entitlement_present` | `False` |
| `pci_transport_entitlement_present` | `False` |
| `real_driverkit_dext_built` | `False` |

## Remediation

- If real DriverKit dext built: `rerun_signing_preflight_then_phase60i`
- If not built: `phase60m-xcode-driverkit-project-materialization-plan`
