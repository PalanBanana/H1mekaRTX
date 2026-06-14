# Compile-Only Failure Sanitizer Summary

- Generated At UTC: `2026-06-14T02:20:01.243037+00:00`
- Compile-Only Failure Sanitizer Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Local Input Present: `True`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
- Private Text Committed: `False`
- Build Artifact Created: `False`
- Signing Attempted: `False`
- Install Attempted: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Sanitized Command Summary

| Command Key | Available | Return Code | Failed | Stdout Present | Stderr Present |
| --- | --- | --- | --- | --- | --- |
| `driverkit_cpp_fsyntax_only` | `True` | `1` | `True` | `False` | `True` |
| `host_swift_typecheck` | `True` | `0` | `False` | `False` | `False` |

## Sanitized Plist Summary

| Path | Present | Parse OK | Error Present |
| --- | --- | --- | --- |
| `tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/H1mekaRTXDriver.entitlements` | `True` | `True` | `False` |
| `tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Info.plist` | `True` | `True` | `False` |
| `tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.entitlements` | `True` | `True` | `False` |
| `tools/driverkit-buildable-scaffold/H1mekaRTXHost/Info.plist` | `True` | `True` | `False` |

## Derived Summary

{
  "all_raw_output_local_only": true,
  "any_compile_command_failed": true,
  "compile_failures_allowed_at_preflight_stage": true,
  "compile_only_attempts_recorded": true,
  "plist_parse_all_ok": true
}
