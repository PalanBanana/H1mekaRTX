# Redacted Export Bundle Assembly Dry-Run Manifest

- Decision: `PASS_REDACTED_EXPORT_BUNDLE_ASSEMBLY_DRY_RUN_MANIFEST_READY`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Assembly Dry-Run Manifest Only: `True`
- Assembly Count: `9`
- Assembly All Sources Exist: `True`
- Assembly All Source Paths Relative: `True`
- Assembly All Bundle Paths Relative: `True`
- Assembly Forbidden Absent: `True`
- Assembly All Not Copied: `True`
- Private Paths Absent: `True`
- FAIL Count: `0`
- Redacted Export Bundle Assembly Dry-Run Manifest Ready: `True`
- Bundle Archive Created By This Phase: `False`
- Files Copied To Export Bundle By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase63i-redacted-bundle-assembly-dry-run-consistency-gate`

## Assembly Entries

| Source Relative Path | Planned Bundle Relative Path | Source Exists | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| `docs/hackintosh/driverkit-entitlement-request-notes-template.md` | `H1mekaRTX-redacted-entitlement-request-dry-run/docs/hackintosh/driverkit-entitlement-request-notes-template.md` | `True` | `1090` | `2cdf0e0c219feced4f545f23eb8a49f8d411e1703e9dde56421468efccec7b1a` |
| `release-readiness/entitlement-request-package-skeleton.md` | `H1mekaRTX-redacted-entitlement-request-dry-run/release-readiness/entitlement-request-package-skeleton.md` | `True` | `2103` | `7db6086b13ceb86b0b255e8ea09232c5c6505eb5669dad2e15024cf14c823a99` |
| `release-readiness/entitlement-request-evidence-checklist.md` | `H1mekaRTX-redacted-entitlement-request-dry-run/release-readiness/entitlement-request-evidence-checklist.md` | `True` | `2330` | `8499a98bdcb8ff775a84b05b0f02f42dda93c170ad44257364bbc32a579d72d4` |
| `release-readiness/entitlement-request-package-consistency-gate.md` | `H1mekaRTX-redacted-entitlement-request-dry-run/release-readiness/entitlement-request-package-consistency-gate.md` | `True` | `2043` | `92f261bc261aea40963a07d1ba3b5d9275f44e6b1c27a8b35342d23003a5bee9` |
| `release-readiness/entitlement-request-pre-submission-packet-ledger.md` | `H1mekaRTX-redacted-entitlement-request-dry-run/release-readiness/entitlement-request-pre-submission-packet-ledger.md` | `True` | `2348` | `926e4c27c11483e6967f35b79e59aa51c5a3681b12033536c1e86f5402f5b95c` |
| `release-readiness/entitlement-request-local-submission-readiness-gate.md` | `H1mekaRTX-redacted-entitlement-request-dry-run/release-readiness/entitlement-request-local-submission-readiness-gate.md` | `True` | `2431` | `77793248e780de09dccb04bc9c94fc63342ad418b2398665c8c5389ae970640d` |
| `release-readiness/manual-entitlement-request-packet-export-checklist.md` | `H1mekaRTX-redacted-entitlement-request-dry-run/release-readiness/manual-entitlement-request-packet-export-checklist.md` | `True` | `2645` | `a5f770371ec855c14ebd5619da788b411214f6c47b1bfa0ffdb45a6f29d43d66` |
| `release-readiness/redacted-manual-export-bundle-manifest.md` | `H1mekaRTX-redacted-entitlement-request-dry-run/release-readiness/redacted-manual-export-bundle-manifest.md` | `True` | `3545` | `c101dd86a1c39704160c3901781780aedb2700aa0dd79e9c54d5bae7e80f77e2` |
| `release-readiness/redacted-bundle-manifest-consistency-gate.md` | `H1mekaRTX-redacted-entitlement-request-dry-run/release-readiness/redacted-bundle-manifest-consistency-gate.md` | `True` | `3111` | `c2f2edba4628e2aeabb16c0194e9c554673f50f9cb6286334578fcf3bd8f4a44` |

## Checks

| Item | Status |
| --- | --- |
| `inventory_consistency_gate_passed` | `PASS` |
| `inventory_consistency_gate_check_passed` | `PASS` |
| `inventory_consistency_gate_ready` | `PASS` |
| `inventory_ledger_ready` | `PASS` |
| `dry_run_plan_ready` | `PASS` |
| `assembly_present` | `PASS` |
| `assembly_count_matches_inventory_count` | `PASS` |
| `assembly_all_sources_exist` | `PASS` |
| `assembly_all_source_paths_relative` | `PASS` |
| `assembly_all_bundle_paths_relative` | `PASS` |
| `assembly_forbidden_absent` | `PASS` |
| `assembly_all_not_copied` | `PASS` |
| `assembly_sha256_present` | `PASS` |
| `assembly_byte_count_present` | `PASS` |
| `private_paths_absent` | `PASS` |
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
| `absolute_paths_recorded_false` | `PASS` |
