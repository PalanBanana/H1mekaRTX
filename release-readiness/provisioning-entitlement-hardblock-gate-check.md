# Provisioning Entitlement Hardblock Gate Check

- Decision: `PASS_PROVISIONING_ENTITLEMENT_HARDBLOCK_GATE_READY`
- Paid Developer Team Required: `True`
- Personal Team Blocked: `True`
- DriverKit Entitlement Approval Required: `True`
- System Extension Capability Required: `True`
- DriverKit PCI Transport Entitlement Required: `True`
- Host Profile Required: `True`
- Dext Profile Required: `True`
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
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/provisioning-entitlement-hardblock-gate.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/provisioning-entitlement-hardblock-gate.md |
| `phase60l_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/real-driverkit-dext-build-gate.json |
| `phase60k_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/validationfailed-root-cause-gate.json |
| `manifest_schema` | PASS | manifest schema |
| `phase60l_schema` | PASS | phase60l schema |
| `phase60k_schema` | PASS | phase60k schema |
| `manifest_provisioning_entitlement_hardblock_gate_ready_true` | PASS | provisioning_entitlement_hardblock_gate_ready |
| `manifest_paid_developer_team_required_true` | PASS | paid_developer_team_required |
| `manifest_personal_team_blocked_true` | PASS | personal_team_blocked |
| `manifest_driverkit_entitlement_approval_required_true` | PASS | driverkit_entitlement_approval_required |
| `manifest_system_extension_capability_required_true` | PASS | system_extension_capability_required |
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
| `doc_contains_Please_enable_Driverkit` | PASS | Please enable Driverkit |
| `doc_contains_Personal_development_teams_do_not_support_the_System_Extension_capability` | PASS | Personal development teams do not support the System Extension capability |
| `doc_contains_paid_Apple_Developer_Program` | PASS | paid Apple Developer Program |
| `doc_contains_DriverKit_entitlement_approval` | PASS | DriverKit entitlement approval |
| `doc_contains_System_Extension_capability` | PASS | System Extension capability |
| `doc_contains_PCI_transport_entitlement` | PASS | PCI transport entitlement |
| `doc_contains_provider_open_remains_blocked` | PASS | provider open remains blocked |
| `doc_contains_GPU_command_submission` | PASS | GPU command submission |
| `doc_contains_Dock_transparency_blur` | PASS | Dock/transparency/blur |
