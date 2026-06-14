import Foundation
import SystemExtensions

final class H1mekaRTXSystemExtensionDelegate: NSObject, OSSystemExtensionRequestDelegate {
    func requestNeedsUserApproval(_ request: OSSystemExtensionRequest) {
        print("H1mekaRTX: request needs user approval")
        print("H1mekaRTX: approve only if you intentionally started this local test")
    }

    func request(_ request: OSSystemExtensionRequest, didFinishWithResult result: OSSystemExtensionRequest.Result) {
        print("H1mekaRTX: request finished: \(result.rawValue)")
        CFRunLoopStop(CFRunLoopGetMain())
    }

    func request(_ request: OSSystemExtensionRequest, didFailWithError error: Error) {
        print("H1mekaRTX: request failed: \(error.localizedDescription)")
        CFRunLoopStop(CFRunLoopGetMain())
    }

    func request(_ request: OSSystemExtensionRequest, actionForReplacingExtension existing: OSSystemExtensionProperties, withExtension replacement: OSSystemExtensionProperties) -> OSSystemExtensionRequest.ReplacementAction {
        print("H1mekaRTX: replacement requested")
        return .replace
    }
}

enum H1mekaRTXHostMode: String {
    case statusOnly = "status-only"
    case dryRun = "dry-run"
    case submitActivation = "submit-activation"
    case submitDeactivation = "submit-deactivation"
}

let extensionIdentifier = "dev.h1meka.H1mekaRTXDriver"
let args = CommandLine.arguments

let mode: H1mekaRTXHostMode
if args.contains("--submit-activation") {
    mode = .submitActivation
} else if args.contains("--submit-deactivation") {
    mode = .submitDeactivation
} else if args.contains("--dry-run") {
    mode = .dryRun
} else {
    mode = .statusOnly
}

print("H1mekaRTXHost")
print("mode=\(mode.rawValue)")
print("extensionIdentifier=\(extensionIdentifier)")
print("providerOpenAttempted=false")
print("barMappingAttempted=false")
print("barMmioMutationAttempted=false")
print("gpuCommandSubmissionAttempted=false")
print("uiCompositorProofClaimed=false")
print("metalProofClaimed=false")

let delegate = H1mekaRTXSystemExtensionDelegate()

switch mode {
case .statusOnly:
    print("activationRequestSubmitted=false")
    print("deactivationRequestSubmitted=false")
    print("status-only: no OSSystemExtensionRequest submitted")

case .dryRun:
    print("activationRequestSubmitted=false")
    print("deactivationRequestSubmitted=false")
    print("dry-run: request object not created and not submitted")

case .submitActivation:
    print("activationRequestSubmitted=true")
    print("deactivationRequestSubmitted=false")
    print("official SystemExtensions activation request path")
    let request = OSSystemExtensionRequest.activationRequest(forExtensionWithIdentifier: extensionIdentifier, queue: .main)
    request.delegate = delegate
    OSSystemExtensionManager.shared.submitRequest(request)
    CFRunLoopRun()

case .submitDeactivation:
    print("activationRequestSubmitted=false")
    print("deactivationRequestSubmitted=true")
    print("official SystemExtensions deactivation request path")
    let request = OSSystemExtensionRequest.deactivationRequest(forExtensionWithIdentifier: extensionIdentifier, queue: .main)
    request.delegate = delegate
    OSSystemExtensionManager.shared.submitRequest(request)
    CFRunLoopRun()
}
