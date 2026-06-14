import Foundation
import SystemExtensions

final class H1mekaRTXSystemExtensionDelegate: NSObject, OSSystemExtensionRequestDelegate {
    func requestNeedsUserApproval(_ request: OSSystemExtensionRequest) {
        print("H1mekaRTX: activation requires user approval")
    }

    func request(_ request: OSSystemExtensionRequest, didFinishWithResult result: OSSystemExtensionRequest.Result) {
        print("H1mekaRTX: request finished: \(result.rawValue)")
    }

    func request(_ request: OSSystemExtensionRequest, didFailWithError error: Error) {
        print("H1mekaRTX: request failed: \(error.localizedDescription)")
    }

    func request(_ request: OSSystemExtensionRequest, actionForReplacingExtension existing: OSSystemExtensionProperties, withExtension replacement: OSSystemExtensionProperties) -> OSSystemExtensionRequest.ReplacementAction {
        return .replace
    }
}

enum H1mekaRTXHostMode: String {
    case statusOnly = "status-only"
    case dryRun = "dry-run"
}

let args = CommandLine.arguments
let mode = args.contains("--dry-run") ? H1mekaRTXHostMode.dryRun : H1mekaRTXHostMode.statusOnly

print("H1mekaRTXHost")
print("mode=\(mode.rawValue)")
print("extensionIdentifier=dev.h1meka.H1mekaRTXDriver")
print("activationAttempted=false")
print("deactivationAttempted=false")
print("providerOpenAttempted=false")
print("barMappingAttempted=false")
print("gpuCommandSubmissionAttempted=false")

if mode == .dryRun {
    print("dry-run only: not submitting OSSystemExtensionRequest")
}
