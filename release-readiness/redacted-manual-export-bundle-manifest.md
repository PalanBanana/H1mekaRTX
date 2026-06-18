# Redacted Manual Export Bundle Manifest

- Decision: `PASS_REDACTED_MANUAL_EXPORT_BUNDLE_MANIFEST_READY`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Redacted Manifest Only: `True`
- Manual Export Checklist PASS: `True`
- Manual Export Check PASS: `True`
- Manual Export Checklist Ready: `True`
- Local Submission Readiness Ready: `True`
- Pre-Submission Packet Ready: `True`
- Evidence Checklist Ready: `True`
- Request Notes Template Ready: `True`
- Inputs Safe: `True`
- PASS Count: `11`
- BLOCKED Count: `6`
- PLACEHOLDER Count: `2`
- FAIL Count: `0`
- Redacted Manual Export Bundle Manifest Ready: `True`
- Bundle Archive Created By This Phase: `False`
- Certificates Exported: `False`
- Private Keys Exported: `False`
- Provisioning Assets Exported: `False`
- Raw IORegistry Exported: `False`
- Provider Handles Exported: `False`
- Actual Apple Entitlement Request Submitted: `False`
- Contacted Apple By This Phase: `False`
- DriverKit Entitlement Requested By This Phase: `False`
- DriverKit PCI Entitlement Requested By This Phase: `False`
- DriverKit Entitlement Approved: `False`
- App ID Created By This Phase: `False`
- Provisioning Profile Created By This Phase: `False`
- DriverKit Profile Created: `False`
- DriverKit Profile Ready: `False`
- DriverKit Extension Signed/Loaded/Activated: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase63c-redacted-bundle-manifest-consistency-gate`

## Included Files

| File |
| --- |
| `docs/hackintosh/driverkit-entitlement-request-notes-template.md` |
| `release-readiness/entitlement-request-package-skeleton.md` |
| `release-readiness/entitlement-request-evidence-checklist.md` |
| `release-readiness/entitlement-request-package-consistency-gate.md` |
| `release-readiness/entitlement-request-pre-submission-packet-ledger.md` |
| `release-readiness/entitlement-request-local-submission-readiness-gate.md` |
| `release-readiness/manual-entitlement-request-packet-export-checklist.md` |

## Excluded Patterns

| Excluded |
| --- |
| `HOST_REPORT_BUNDLE_TOKEN` |
| `raw stdout` |
| `raw stderr` |
| `IORegistry raw` |
| `private key` |
| `certificate` |
| `provisioning profile` |
| `PRIVATE_HOME_PATH_TOKEN` |
| `PRIVATE_VAR_FOLDERS_TOKEN` |
| `VAR_FOLDERS_TOKEN` |
| `provider handle` |
| `BAR dump` |
| `MMIO dump` |

## Items

| Item | Status |
| --- | --- |
| `manual_export_checklist_passed` | `PASS` |
| `manual_export_check_passed` | `PASS` |
| `manual_export_checklist_ready` | `PASS` |
| `local_submission_readiness_gate_ready` | `PASS` |
| `pre_submission_packet_ready` | `PASS` |
| `evidence_checklist_ready` | `PASS` |
| `request_notes_template_ready` | `PASS` |
| `future_manual_redaction_required` | `PLACEHOLDER` |
| `future_manual_bundle_creation_required` | `PLACEHOLDER` |
| `bundle_archive_not_created_by_this_phase` | `BLOCKED` |
| `certificates_not_exported` | `BLOCKED` |
| `private_keys_not_exported` | `BLOCKED` |
| `provisioning_assets_not_exported` | `BLOCKED` |
| `raw_ioregistry_not_exported` | `BLOCKED` |
| `actual_apple_submission_not_performed` | `BLOCKED` |
| `provider_open_blocked` | `PASS` |
| `bar_access_blocked` | `PASS` |
| `gpu_command_submission_blocked` | `PASS` |
| `metal_acceleration_not_claimed` | `PASS` |
