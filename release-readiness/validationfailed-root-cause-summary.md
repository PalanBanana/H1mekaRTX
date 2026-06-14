# ValidationFailed Root-Cause Summary

- Generated At UTC: `2026-06-14T04:13:01.457279+00:00`
- Summary Only: `True`
- Applications Decision: `PASS_APPLICATIONS_LOCATION_DELEGATE_FAILED`
- Delegate Error Domain: `OSSystemExtensionErrorDomain`
- Delegate Error Code: `9`
- Phase 61 Allowed Now: `False`
- Provider Open Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Details

| Key | Value |
| --- | --- |
| `delegate_error_domain` | `OSSystemExtensionErrorDomain` |
| `delegate_error_code` | `9` |
| `staged_to_applications` | `True` |
| `activation_submitted` | `True` |
| `codesign_host_valid` | `True` |
| `codesign_dext_valid` | `True` |
| `spctl_host_rejected` | `True` |
| `spctl_dext_rejected` | `True` |
| `apple_development_signature` | `True` |
| `driverkit_entitlement_present` | `True` |
| `pci_transport_entitlement_present` | `True` |
| `dext_plain_macho_executable` | `True` |
| `dext_xcode_driverkit_build_proven` | `False` |
| `developer_mode_on` | `False` |

## Root Causes

| Root Cause |
| --- |
| `spctl_rejected_host_or_dext` |
| `developer_mode_not_confirmed_on` |
| `real_xcode_built_driverkit_dext_binary_not_proven` |
| `driverkit_entitlements_present_but_os_acceptance_not_proven` |
| `apple_development_signed_non_notarized_local_build` |

## Remediation

- Next Gate: `phase60l-real-driverkit-dext-build-gate`
- Local Manual Hint: `enable developer mode for local testing and replace generic C stub with a real Xcode-built DriverKit dext target signed with approved entitlements`
