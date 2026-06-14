# Codesign Dry-Run Command Plan

- Generated At UTC: `2026-06-14T02:35:58.906971+00:00`
- Command Plan Only: `True`
- Codesign Executed: `False`
- Codesign Signing Attempted: `False`
- Signed Package Created: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Planned Commands

| Name | Execute Now | Command |
| --- | --- | --- |
| `sign_embedded_dext` | `False` | `codesign --force --timestamp=none --options runtime --entitlements tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/H1mekaRTXDriver.entitlements --sign SIGNING_IDENTITY_PLACEHOLDER host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext` |
| `verify_embedded_dext` | `False` | `codesign --verify --strict --verbose=4 host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext` |
| `sign_host_app` | `False` | `codesign --force --timestamp=none --options runtime --entitlements tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.entitlements --sign SIGNING_IDENTITY_PLACEHOLDER host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app` |
| `verify_host_app` | `False` | `codesign --verify --strict --verbose=4 host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app` |
| `dump_host_entitlements` | `False` | `codesign -d --entitlements :- host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app` |
| `dump_dext_entitlements` | `False` | `codesign -d --entitlements :- host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext` |
| `capture_systemextensionsctl_status_before_activation` | `False` | `systemextensionsctl list` |

## Derived

| Key | Value |
| --- | --- |
| `command_count` | `7` |
| `all_commands_marked_execute_now_false` | `True` |
| `contains_sign_embedded_dext` | `True` |
| `contains_verify_embedded_dext` | `True` |
| `contains_sign_host_app` | `True` |
| `contains_verify_host_app` | `True` |
| `contains_entitlement_dump` | `True` |
| `contains_systemextensionsctl_status_capture` | `True` |
