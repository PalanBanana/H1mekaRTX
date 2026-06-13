//
// H1mekaRTXSystemExtensionActivationDryRun.swift
//
// Phase 20 static skeleton only.
// Default mode is dry-run.
// This file must not be treated as a built, signed, installed, or activated System Extension host app.
//
// Safety:
// - No DriverKit activation in this phase.
// - No System Extension activation in this phase.
// - No System Extension deactivation in this phase.
// - No dext load in this phase.
// - No provider open.
// - No BAR mapping.
// - No BAR/MMIO mutation.
// - No GPU command submission.
// - No direct Dock injection.
// - No WindowServer patching.
//
// Future note:
// Real OSSystemExtensionRequest activation/deactivation submit must be introduced only after
// activation prerequisites ledger says every required item is READY.
//

import Foundation

#if canImport(SystemExtensions)
import SystemExtensions
#endif

enum H1mekaRTXActivationMode: String {
    case dryRunActivate = "dry-run-activate"
    case dryRunDeactivate = "dry-run-deactivate"
    case statusPlan = "status-plan"
}

struct H1mekaRTXActivationPlan {
    static let extensionIdentifier = "dev.h1meka.H1mekaRTXDriver"
    static let defaultMode = H1mekaRTXActivationMode.statusPlan
    static let realActivationAttempted = false
    static let realDeactivationAttempted = false
    static let providerOpenAttempted = false
    static let barMappingAttempted = false
    static let gpuCommandSubmissionAttempted = false
}

final class H1mekaRTXSystemExtensionActivationDryRun {
    func run(mode: H1mekaRTXActivationMode) -> Int32 {
        switch mode {
        case .dryRunActivate:
            return dryRunActivate()
        case .dryRunDeactivate:
            return dryRunDeactivate()
        case .statusPlan:
            return statusPlan()
        }
    }

    private func dryRunActivate() -> Int32 {
        print("DRY RUN: would prepare OSSystemExtensionRequest.activationRequest for \(H1mekaRTXActivationPlan.extensionIdentifier)")
        print("DRY RUN: request is not submitted in Phase 20")
        print("DRY RUN: no provider open, no BAR mapping, no GPU command submission")
        return 0
    }

    private func dryRunDeactivate() -> Int32 {
        print("DRY RUN: would prepare OSSystemExtensionRequest.deactivationRequest for \(H1mekaRTXActivationPlan.extensionIdentifier)")
        print("DRY RUN: request is not submitted in Phase 20")
        print("DRY RUN: rollback/deactivation remains future gated")
        return 0
    }

    private func statusPlan() -> Int32 {
        print("H1mekaRTX Phase 20 activation/deactivation dry-run skeleton")
        print("extensionIdentifier=\(H1mekaRTXActivationPlan.extensionIdentifier)")
        print("realActivationAttempted=\(H1mekaRTXActivationPlan.realActivationAttempted)")
        print("realDeactivationAttempted=\(H1mekaRTXActivationPlan.realDeactivationAttempted)")
        print("providerOpenAttempted=\(H1mekaRTXActivationPlan.providerOpenAttempted)")
        print("barMappingAttempted=\(H1mekaRTXActivationPlan.barMappingAttempted)")
        print("gpuCommandSubmissionAttempted=\(H1mekaRTXActivationPlan.gpuCommandSubmissionAttempted)")
        return 0
    }
}

// Intentionally no top-level activation submit.
// Future phases may add guarded execution only after ledger READY.
