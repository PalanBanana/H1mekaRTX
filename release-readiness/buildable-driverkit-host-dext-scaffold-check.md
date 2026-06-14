# Buildable DriverKit Host + Dext Scaffold Check

- Decision: `PASS_BUILDABLE_DRIVERKIT_HOST_DEXT_SCAFFOLD_READY`
- Real Development Build Scope Started: `True`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

| Check | Status | Detail |
| --- | --- | --- |
| `exists_tools_driverkit-buildable-scaffold_buildable-driverkit-host-dext-scaffold.json` | PASS | tools/driverkit-buildable-scaffold/buildable-driverkit-host-dext-scaffold.json |
| `exists_tools_driverkit-buildable-scaffold_build-plan.json` | PASS | tools/driverkit-buildable-scaffold/build-plan.json |
| `exists_tools_driverkit-buildable-scaffold_H1mekaRTXHost_Info.plist` | PASS | tools/driverkit-buildable-scaffold/H1mekaRTXHost/Info.plist |
| `exists_tools_driverkit-buildable-scaffold_H1mekaRTXHost_H1mekaRTXHost.swift` | PASS | tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.swift |
| `exists_tools_driverkit-buildable-scaffold_H1mekaRTXHost_H1mekaRTXHost.entitlements` | PASS | tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.entitlements |
| `exists_tools_driverkit-buildable-scaffold_H1mekaRTXDriver.dext_Info.plist` | PASS | tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Info.plist |
| `exists_tools_driverkit-buildable-scaffold_H1mekaRTXDriver.dext_H1mekaRTXDriver.entitlements` | PASS | tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/H1mekaRTXDriver.entitlements |
| `exists_tools_driverkit-buildable-scaffold_H1mekaRTXDriver.dext_Sources_H1mekaRTXDriver.cpp` | PASS | tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Sources/H1mekaRTXDriver.cpp |
| `exists_docs_driverkit_buildable-driverkit-host-dext-scaffold.md` | PASS | docs/driverkit/buildable-driverkit-host-dext-scaffold.md |
| `manifest_schema` | PASS | manifest schema |
| `build_plan_schema` | PASS | build plan schema |
| `host_bundle_id` | PASS | host bundle id |
| `dext_bundle_id` | PASS | dext bundle id |
| `iopcimatch_5070` | PASS | 0x2f0410de |
| `provider_class_iopci` | PASS | IOPCIDevice |
| `host_system_extension_entitlement` | PASS | host entitlement |
| `dext_driverkit_entitlement` | PASS | driverkit entitlement |
| `dext_pci_entitlement_present` | PASS | pci entitlement |
| `host_dry_run_no_submit` | PASS | dry run only |
| `dext_no_runtime_access_comment` | PASS | runtime forbidden comment |
| `manifest_system_extension_activation_attempted_false` | PASS | system_extension_activation_attempted |
| `manifest_system_extension_deactivation_attempted_false` | PASS | system_extension_deactivation_attempted |
| `manifest_dext_load_attempted_false` | PASS | dext_load_attempted |
| `manifest_provider_open_attempted_false` | PASS | provider_open_attempted |
| `manifest_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `manifest_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `manifest_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `manifest_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `manifest_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `manifest_metal_proof_claimed_false` | PASS | metal_proof_claimed |
