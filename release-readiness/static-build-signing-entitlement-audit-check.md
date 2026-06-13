# Static Build / Signing / Entitlement Audit Report

- Generated At UTC: `2026-06-13T15:45:11.617202+00:00`
- Decision: `PASS_STATIC_BUILD_SIGNING_ENTITLEMENT_AUDIT_READY`
- Classification: `CLASSIFICATION_STATIC_BUILD_SIGNING_ENTITLEMENT_AUDIT`
- Secondary Classification: `CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT`
- Scope: `Phase 10 static build/signing/entitlement audit gate`
- Static Audit Only: `True`
- Build Attempted: `False`
- Signing Attempted: `False`
- Install Attempted: `False`
- DriverKit Activation Attempted: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Device Ownership Request Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR/MMIO Mutation Attempted: `False`
- Real GPU Command Execution Attempted: `False`
- RTX 5070 Workload Attribution Claimed: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Bundle / Entitlement Contract

| Field | Value |
| --- | --- |
| host_bundle_id | dev.h1meka.H1mekaRTXHost |
| dext_bundle_id | dev.h1meka.H1mekaRTXDriver |
| dext_extension_point | com.apple.driverkit |
| io_pci_match | 0x2f0410de |
| provider_class | IOPCIDevice |
| expected_system_extension_entitlement | com.apple.developer.system-extension.install |
| expected_driverkit_entitlement | com.apple.developer.driverkit |
| expected_pci_transport_entitlement | com.apple.developer.driverkit.transport.pci |

## Target User-Visible UI Goal

This audit preserves the Hackintosh RTX 5070 macOS UI compositor target:

- Dock animation
- Dock magnification
- transparency
- blur
- window movement
- window resizing
- Mission Control
- Launchpad
- Stage Manager

No UI acceleration success is claimed in this phase.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
| `contract_file_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/static-build-signing-entitlement-audit-gate.md |
| `host_info_plist_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-skeleton/H1mekaRTXHost.app.template/Info.plist |
| `dext_info_plist_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-skeleton/H1mekaRTXDriver.dext.template/Info.plist |
| `host_entitlements_template_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-skeleton/H1mekaRTXHost.entitlements.template.plist |
| `dext_entitlements_template_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-skeleton/H1mekaRTXDriver.entitlements.template.plist |
| `requires_token_classification_static_build_signing_entitlement_audit` | PASS | CLASSIFICATION_STATIC_BUILD_SIGNING_ENTITLEMENT_AUDIT |
| `requires_token_classification_driverkit_feasibility_preflight` | PASS | CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT |
| `requires_token_classification_static_contract` | PASS | CLASSIFICATION_STATIC_CONTRACT |
| `requires_token_static_audit_only_true` | PASS | STATIC_AUDIT_ONLY: True |
| `requires_token_no_build_attempted_true` | PASS | NO_BUILD_ATTEMPTED: True |
| `requires_token_no_signing_attempted_true` | PASS | NO_SIGNING_ATTEMPTED: True |
| `requires_token_no_install_attempted_true` | PASS | NO_INSTALL_ATTEMPTED: True |
| `requires_token_no_driver_activation_true` | PASS | NO_DRIVER_ACTIVATION: True |
| `requires_token_no_system_extension_activation_true` | PASS | NO_SYSTEM_EXTENSION_ACTIVATION: True |
| `requires_token_no_dext_load_true` | PASS | NO_DEXT_LOAD: True |
| `requires_token_no_device_ownership_request_true` | PASS | NO_DEVICE_OWNERSHIP_REQUEST: True |
| `requires_token_no_provider_open_true` | PASS | NO_PROVIDER_OPEN: True |
| `requires_token_no_bar_mapping_true` | PASS | NO_BAR_MAPPING: True |
| `requires_token_no_bar_mmio_mutation_true` | PASS | NO_BAR_MMIO_MUTATION: True |
| `requires_token_no_command_submission_true` | PASS | NO_COMMAND_SUBMISSION: True |
| `requires_token_no_gsp_firmware_load_true` | PASS | NO_GSP_FIRMWARE_LOAD: True |
| `requires_token_no_gpu_reset_true` | PASS | NO_GPU_RESET: True |
| `requires_token_no_framebuffer_init_true` | PASS | NO_FRAMEBUFFER_INIT: True |
| `requires_token_no_display_engine_init_true` | PASS | NO_DISPLAY_ENGINE_INIT: True |
| `requires_token_no_kernel_or_process_injection_true` | PASS | NO_KERNEL_OR_PROCESS_INJECTION: True |
| `requires_token_no_sip_amfi_bypass_true` | PASS | NO_SIP_AMFI_BYPASS: True |
| `requires_token_no_private_framework_patching_true` | PASS | NO_PRIVATE_FRAMEWORK_PATCHING: True |
| `requires_token_no_fake_metal_device_spoofing_true` | PASS | NO_FAKE_METAL_DEVICE_SPOOFING: True |
| `requires_token_static_build_signing_entitlement_audit_inputs` | PASS | STATIC_BUILD_SIGNING_ENTITLEMENT_AUDIT_INPUTS |
| `requires_token_bundle_identity_contract` | PASS | BUNDLE_IDENTITY_CONTRACT |
| `requires_token_target_pci_provider_matching_manifest` | PASS | TARGET_PCI_PROVIDER_MATCHING_MANIFEST |
| `requires_token_static_entitlement_audit_checklist` | PASS | STATIC_ENTITLEMENT_AUDIT_CHECKLIST |
| `requires_token_dev.h1meka.h1mekartxhost` | PASS | dev.h1meka.H1mekaRTXHost |
| `requires_token_dev.h1meka.h1mekartxdriver` | PASS | dev.h1meka.H1mekaRTXDriver |
| `requires_token_com.apple.driverkit` | PASS | com.apple.driverkit |
| `requires_token_com.apple.developer.driverkit` | PASS | com.apple.developer.driverkit |
| `requires_token_com.apple.developer.driverkit.transport.pci` | PASS | com.apple.developer.driverkit.transport.pci |
| `requires_token_com.apple.developer.system-extension.install` | PASS | com.apple.developer.system-extension.install |
| `requires_token_nvidia_rtx_5070` | PASS | NVIDIA RTX 5070 |
| `requires_token_0x10de` | PASS | 0x10de |
| `requires_token_0x2f04` | PASS | 0x2f04 |
| `requires_token_0x2f0410de` | PASS | 0x2f0410de |
| `requires_token_windowserver` | PASS | WindowServer |
| `requires_token_core_animation` | PASS | Core Animation |
| `requires_token_quartzcore` | PASS | QuartzCore |
| `requires_token_metal_compositor` | PASS | Metal compositor |
| `requires_token_dock` | PASS | Dock |
| `requires_token_transparency` | PASS | transparency |
| `requires_token_blur` | PASS | blur |
| `requires_token_build_attempted_false` | PASS | BUILD_ATTEMPTED: False |
| `requires_token_signing_attempted_false` | PASS | SIGNING_ATTEMPTED: False |
| `requires_token_install_attempted_false` | PASS | INSTALL_ATTEMPTED: False |
| `requires_token_driverkit_activation_attempted_false` | PASS | DRIVERKIT_ACTIVATION_ATTEMPTED: False |
| `requires_token_system_extension_activation_attempted_false` | PASS | SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False |
| `requires_token_dext_load_attempted_false` | PASS | DEXT_LOAD_ATTEMPTED: False |
| `requires_token_device_ownership_request_attempted_false` | PASS | DEVICE_OWNERSHIP_REQUEST_ATTEMPTED: False |
| `requires_token_provider_open_attempted_false` | PASS | PROVIDER_OPEN_ATTEMPTED: False |
| `requires_token_bar_mapping_attempted_false` | PASS | BAR_MAPPING_ATTEMPTED: False |
| `requires_token_bar_mmio_mutation_attempted_false` | PASS | BAR_MMIO_MUTATION_ATTEMPTED: False |
| `requires_token_real_gpu_command_execution_attempted_false` | PASS | REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False |
| `requires_token_rtx5070_workload_attribution_claimed_false` | PASS | RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False |
| `requires_token_real_gpu_acceleration_claimed_false` | PASS | REAL_GPU_ACCELERATION_CLAIMED: False |
| `requires_token_ui_compositor_proof_claimed_false` | PASS | UI_COMPOSITOR_PROOF_CLAIMED: False |
| `requires_token_metal_proof_claimed_false` | PASS | METAL_PROOF_CLAIMED: False |
| `host_bundle_id_matches` | PASS | dev.h1meka.H1mekaRTXHost |
| `dext_bundle_id_matches` | PASS | dev.h1meka.H1mekaRTXDriver |
| `host_system_extension_entitlement_template_present` | PASS | com.apple.developer.system-extension.install |
| `dext_driverkit_entitlement_template_present` | PASS | com.apple.developer.driverkit |
| `dext_pci_transport_entitlement_template_present` | PASS | com.apple.developer.driverkit.transport.pci |
| `pci_template_vendor_id_present` | PASS | 0x10de |
| `pci_template_device_id_present` | PASS | 0x2f04 |
| `pci_template_iopcimatch_present` | PASS | 0x2f0410de |

## Conclusion

This phase is a static audit only. It does not build, sign, install, activate, load, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.

## Next Phase Recommendation

Next safe step: generate a deterministic Xcode/project-layout contract without building, signing, or activating.
