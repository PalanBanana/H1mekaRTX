# Apple Developer Entitlement Request Checklist Check

- Decision: `PASS_APPLE_DEVELOPER_ENTITLEMENT_REQUEST_CHECKLIST_READY`
- Portal Preparation Only: `True`
- Paid Developer Team Required: `True`
- Personal Team Blocked: `True`
- DriverKit Entitlement Approval Required: `True`
- System Extension Capability Required: `True`
- DriverKit PCI Transport Entitlement Required: `True`
- Phase 61 Allowed Now: `False`
- Xcodebuild Attempted By This Phase: `False`
- Activation Submitted By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/apple-developer-entitlement-request-checklist.json |
| `manual_checklist_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/apple-developer-portal-manual-checklist.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/apple-developer-entitlement-request-checklist.md |
| `phase60q_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/provisioning-entitlement-hardblock-gate.json |
| `manifest_schema` | PASS | manifest schema |
| `manual_schema` | PASS | manual schema |
| `phase60q_schema` | PASS | phase60q schema |
| `manifest_apple_developer_entitlement_request_checklist_ready_true` | PASS | apple_developer_entitlement_request_checklist_ready |
| `manifest_portal_preparation_only_true` | PASS | portal_preparation_only |
| `manifest_paid_developer_team_required_true` | PASS | paid_developer_team_required |
| `manifest_personal_team_blocked_true` | PASS | personal_team_blocked |
| `manifest_system_extension_capability_required_true` | PASS | system_extension_capability_required |
| `manifest_driverkit_entitlement_approval_required_true` | PASS | driverkit_entitlement_approval_required |
| `manifest_driverkit_pci_transport_entitlement_required_true` | PASS | driverkit_pci_transport_entitlement_required |
| `manifest_host_profile_required_true` | PASS | host_profile_required |
| `manifest_dext_profile_required_true` | PASS | dext_profile_required |
| `manifest_xcodebuild_attempted_by_this_phase_false` | PASS | xcodebuild_attempted_by_this_phase |
| `manifest_activation_submitted_by_this_phase_false` | PASS | activation_submitted_by_this_phase |
| `manifest_deactivation_submitted_by_this_phase_false` | PASS | deactivation_submitted_by_this_phase |
| `manifest_install_attempted_false` | PASS | install_attempted |
| `manifest_manual_dext_load_attempted_false` | PASS | manual_dext_load_attempted |
| `manifest_provider_open_attempted_false` | PASS | provider_open_attempted |
| `manifest_ioserviceopen_attempted_false` | PASS | ioserviceopen_attempted |
| `manifest_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `manifest_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `manifest_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `manifest_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `manifest_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `manifest_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `manifest_host_bundle_id` | PASS | host_bundle_id=dev.h1meka.H1mekaRTXHost |
| `manifest_dext_bundle_id` | PASS | dext_bundle_id=dev.h1meka.H1mekaRTXDriver |
| `manifest_system_extension_entitlement` | PASS | system_extension_entitlement=com.apple.developer.system-extension.install |
| `manifest_driverkit_entitlement` | PASS | driverkit_entitlement=com.apple.developer.driverkit |
| `manifest_driverkit_pci_transport_entitlement` | PASS | driverkit_pci_transport_entitlement=com.apple.developer.driverkit.transport.pci |
| `manifest_vendor_id` | PASS | vendor_id=0x10de |
| `manifest_device_id` | PASS | device_id=0x2f04 |
| `manifest_iopcimatch` | PASS | iopcimatch=0x2f0410de |
| `manual_item_paid_team` | PASS | paid_team |
| `manual_item_host_app_id` | PASS | host_app_id |
| `manual_item_host_system_extension_capability` | PASS | host_system_extension_capability |
| `manual_item_dext_app_id` | PASS | dext_app_id |
| `manual_item_driverkit_entitlement` | PASS | driverkit_entitlement |
| `manual_item_driverkit_pci_transport` | PASS | driverkit_pci_transport |
| `manual_item_host_profile` | PASS | host_profile |
| `manual_item_dext_profile` | PASS | dext_profile |
| `doc_contains_Paid_Apple_Developer_Program` | PASS | Paid Apple Developer Program |
| `doc_contains_dev.h1meka.H1mekaRTXHost` | PASS | dev.h1meka.H1mekaRTXHost |
| `doc_contains_dev.h1meka.H1mekaRTXDriver` | PASS | dev.h1meka.H1mekaRTXDriver |
| `doc_contains_com.apple.developer.system-extension.install` | PASS | com.apple.developer.system-extension.install |
| `doc_contains_com.apple.developer.driverkit` | PASS | com.apple.developer.driverkit |
| `doc_contains_com.apple.developer.driverkit.transport.pci` | PASS | com.apple.developer.driverkit.transport.pci |
| `doc_contains_0x10de` | PASS | 0x10de |
| `doc_contains_0x2f04` | PASS | 0x2f04 |
| `doc_contains_0x2f0410de` | PASS | 0x2f0410de |
| `doc_contains_provider_open_remains_blocked` | PASS | provider open remains blocked |
| `doc_contains_GPU_command_submission_remains_blocked` | PASS | GPU command submission remains blocked |
| `doc_contains_Dock_transparency_blur_proof_remains_blocked` | PASS | Dock/transparency/blur proof remains blocked |
