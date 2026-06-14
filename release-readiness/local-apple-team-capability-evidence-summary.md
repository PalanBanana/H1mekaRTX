# Local Apple Team Capability Evidence Summary

- Generated At UTC: `2026-06-14T04:42:13.082773+00:00`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Local Evidence Report Present: `True`
- Phase 61 Allowed Now: `False`
- Provider Open Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Evidence

| Key | Value |
| --- | --- |
| `xcode_present` | `True` |
| `driverkit_sdk_present` | `True` |
| `macosx_sdk_present` | `True` |
| `apple_development_identity_present` | `True` |
| `xcode_project_present` | `True` |
| `personal_team_blocker_observed` | `True` |
| `system_extension_capability_blocker_observed` | `True` |
| `driverkit_enable_blocker_observed` | `True` |
| `host_profile_missing_observed` | `True` |
| `dext_profile_missing_observed` | `True` |
| `paid_team_proven` | `False` |
| `driverkit_entitlement_approval_proven` | `False` |
| `pci_transport_entitlement_approval_proven` | `False` |
| `system_extension_capability_proven` | `False` |
| `phase61_allowed_now` | `False` |

## Remediation

- If paid team and entitlements are proven: `rerun_phase60l_real_driverkit_dext_build_gate`
- If not proven: `wait_for_paid_team_and_apple_entitlement_approval`
