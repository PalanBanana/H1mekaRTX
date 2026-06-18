# Redacted Export Bundle Dry-Run Inventory Ledger

- Decision: `PASS_REDACTED_EXPORT_BUNDLE_DRY_RUN_INVENTORY_LEDGER_READY`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Dry-Run Inventory Ledger Only: `True`
- Plan Consistency Gate PASS: `True`
- Plan Consistency Gate Check PASS: `True`
- Plan Consistency Gate Ready: `True`
- Dry-Run Plan Ready: `True`
- Manifest Consistency Gate Ready: `True`
- Redacted Manifest Ready: `True`
- Inventory Count: `9`
- Inventory All Exist: `True`
- Inventory All Relative: `True`
- Inventory Forbidden Absent: `True`
- Inventory All Not Copied: `True`
- Exclude Labels Present: `True`
- Inputs Safe: `True`
- PASS Count: `34`
- FAIL Count: `0`
- Redacted Export Bundle Dry-Run Inventory Ledger Ready: `True`
- Bundle Archive Created By This Phase: `False`
- Files Copied To Export Bundle By This Phase: `False`
- Certificates Exported: `False`
- Private Keys Exported: `False`
- Provisioning Assets Exported: `False`
- Raw IORegistry Exported: `False`
- Provider Handles Exported: `False`
- Actual Apple Entitlement Request Submitted: `False`
- Contacted Apple By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase63g-redacted-export-inventory-consistency-gate`

## Inventory

| Relative Path | Exists | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `docs/hackintosh/driverkit-entitlement-request-notes-template.md` | `True` | `1090` | `2cdf0e0c219feced4f545f23eb8a49f8d411e1703e9dde56421468efccec7b1a` |
| `release-readiness/entitlement-request-package-skeleton.md` | `True` | `2103` | `7db6086b13ceb86b0b255e8ea09232c5c6505eb5669dad2e15024cf14c823a99` |
| `release-readiness/entitlement-request-evidence-checklist.md` | `True` | `2330` | `8499a98bdcb8ff775a84b05b0f02f42dda93c170ad44257364bbc32a579d72d4` |
| `release-readiness/entitlement-request-package-consistency-gate.md` | `True` | `2043` | `92f261bc261aea40963a07d1ba3b5d9275f44e6b1c27a8b35342d23003a5bee9` |
| `release-readiness/entitlement-request-pre-submission-packet-ledger.md` | `True` | `2348` | `926e4c27c11483e6967f35b79e59aa51c5a3681b12033536c1e86f5402f5b95c` |
| `release-readiness/entitlement-request-local-submission-readiness-gate.md` | `True` | `2431` | `77793248e780de09dccb04bc9c94fc63342ad418b2398665c8c5389ae970640d` |
| `release-readiness/manual-entitlement-request-packet-export-checklist.md` | `True` | `2645` | `a5f770371ec855c14ebd5619da788b411214f6c47b1bfa0ffdb45a6f29d43d66` |
| `release-readiness/redacted-manual-export-bundle-manifest.md` | `True` | `3545` | `c101dd86a1c39704160c3901781780aedb2700aa0dd79e9c54d5bae7e80f77e2` |
| `release-readiness/redacted-bundle-manifest-consistency-gate.md` | `True` | `3111` | `c2f2edba4628e2aeabb16c0194e9c554673f50f9cb6286334578fcf3bd8f4a44` |

## Checks

| Item | Status |
| --- | --- |
| `plan_consistency_gate_passed` | `PASS` |
| `plan_consistency_gate_check_passed` | `PASS` |
| `plan_consistency_gate_ready` | `PASS` |
| `dry_run_plan_ready` | `PASS` |
| `manifest_consistency_gate_ready` | `PASS` |
| `redacted_manifest_ready` | `PASS` |
| `inventory_present` | `PASS` |
| `inventory_all_exist` | `PASS` |
| `inventory_all_relative` | `PASS` |
| `inventory_forbidden_absent` | `PASS` |
| `inventory_all_not_copied` | `PASS` |
| `exclude_labels_present` | `PASS` |
| `bundle_archive_created_by_this_phase_false` | `PASS` |
| `files_copied_to_export_bundle_by_this_phase_false` | `PASS` |
| `certificates_exported_false` | `PASS` |
| `private_keys_exported_false` | `PASS` |
| `provisioning_assets_exported_false` | `PASS` |
| `raw_ioregistry_exported_false` | `PASS` |
| `provider_handles_exported_false` | `PASS` |
| `actual_apple_entitlement_request_submitted_false` | `PASS` |
| `contacted_apple_by_this_phase_false` | `PASS` |
| `provider_open_attempted_false` | `PASS` |
| `ioserviceopen_attempted_false` | `PASS` |
| `bar_mapping_attempted_false` | `PASS` |
| `bar0_read_attempted_false` | `PASS` |
| `bar0_write_attempted_false` | `PASS` |
| `gpu_command_submission_attempted_false` | `PASS` |
| `current_rtx5070_metal_acceleration_claimed_false` | `PASS` |
| `dock_transparency_blur_acceleration_claimed_false` | `PASS` |
| `vendor_id` | `PASS` |
| `device_id` | `PASS` |
| `iopcimatch` | `PASS` |
| `driverkit_bundle_identifier` | `PASS` |
| `host_app_bundle_identifier` | `PASS` |
