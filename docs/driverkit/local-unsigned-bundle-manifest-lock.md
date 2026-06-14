# Local Unsigned Bundle Manifest Lock

## Purpose

Phase 51 records a local-only manifest lock for the unsigned host app bundle layout.

This phase locks the local unsigned bundle file list, relative paths, sizes, modes, and SHA-256 hashes.

This phase is manifest-lock evidence only.

This phase may generate the local unsigned app bundle under host-report-bundle if missing.

This phase may read local files under host-report-bundle.

This phase commits only sanitized release-readiness summaries.

This phase does not create signed artifacts.

This phase does not codesign anything.

This phase does not install anything.

This phase does not submit an activation request.

This phase does not submit a deactivation request.

This phase does not load a dext.

This phase does not open a provider.

This phase does not map BAR memory.

This phase does not mutate BAR/MMIO.

This phase does not write PCI configuration space.

This phase does not load firmware.

This phase does not reset the GPU.

This phase does not initialize framebuffer or display-engine paths.

This phase does not submit GPU commands.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Locked Local-Only Layout

Expected local-only layout root:

- host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app

Expected bundle entries:

- H1mekaRTXHost.app/Contents/Info.plist
- H1mekaRTXHost.app/Contents/MacOS/H1mekaRTXHost.placeholder
- H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/Info.plist
- H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/MacOS/H1mekaRTXDriver.placeholder

## Committed Outputs

- release-readiness/local-unsigned-bundle-manifest-lock-summary.json
- release-readiness/local-unsigned-bundle-manifest-lock-summary.md
- release-readiness/local-unsigned-bundle-manifest-lock-check.json
- release-readiness/local-unsigned-bundle-manifest-lock-check.md

## Local-Only Outputs

- host-report-bundle/unsigned-app-bundle-manifest-lock/local-unsigned-bundle-manifest-lock.json
- host-report-bundle/unsigned-app-bundle-manifest-lock/local-unsigned-bundle-manifest-lock.md

## Classification

- CLASSIFICATION_LOCAL_UNSIGNED_BUNDLE_MANIFEST_LOCK
- CLASSIFICATION_UNSIGNED_LOCAL_APP_BUNDLE_LAYOUT_GENERATOR
- CLASSIFICATION_NO_SIGNING_NO_INSTALL_NO_ACTIVATION
- CLASSIFICATION_LOCAL_EVIDENCE_ONLY

## Current State

- LOCAL_UNSIGNED_BUNDLE_MANIFEST_LOCK_READY: True
- MANIFEST_LOCK_ONLY: True
- LOCAL_EVIDENCE_ONLY: True
- HOST_REPORT_BUNDLE_LOCAL_ONLY: True
- SIGNED_PACKAGE_CREATED: False
- CODESIGN_ATTEMPTED: False
- INSTALL_ATTEMPTED: False
- SUBMIT_ACTIVATION_ALLOWED_NOW: False
- SUBMIT_DEACTIVATION_ALLOWED_NOW: False
- SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False
- SYSTEM_EXTENSION_DEACTIVATION_ATTEMPTED: False
- DEXT_LOAD_ATTEMPTED: False
- PROVIDER_OPEN_ATTEMPTED: False
- BAR_MAPPING_ATTEMPTED: False
- BAR_MMIO_MUTATION_ATTEMPTED: False
- CONFIGURATION_WRITES_ATTEMPTED: False
- GPU_COMMAND_SUBMISSION_ATTEMPTED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
