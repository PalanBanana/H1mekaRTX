import Foundation
import SystemExtensions

final class H1mekaRTXHostDelegate: NSObject, OSSystemExtensionRequestDelegate {
    func requestNeedsUserApproval(_ request: OSSystemExtensionRequest) {
        print("H1MEKARTX_HOST_EVENT=request_needs_user_approval")
    }

    func request(_ request: OSSystemExtensionRequest, didFinishWithResult result: OSSystemExtensionRequest.Result) {
        print("H1MEKARTX_HOST_EVENT=did_finish")
        print("H1MEKARTX_HOST_RESULT=\(result)")
    }

    func request(_ request: OSSystemExtensionRequest, didFailWithError error: Error) {
        let nsError = error as NSError
        print("H1MEKARTX_HOST_EVENT=did_fail")
        print("H1MEKARTX_HOST_ERROR_DOMAIN=\(nsError.domain)")
        print("H1MEKARTX_HOST_ERROR_CODE=\(nsError.code)")
        print("H1MEKARTX_HOST_ERROR_DESCRIPTION=\(nsError.localizedDescription)")
    }

    func request(_ request: OSSystemExtensionRequest, actionForReplacingExtension existing: OSSystemExtensionProperties, withExtension ext: OSSystemExtensionProperties) -> OSSystemExtensionRequest.ReplacementAction {
        print("H1MEKARTX_HOST_EVENT=replacement_requested")
        return .replace
    }
}

let args = CommandLine.arguments
let extensionID = "dev.h1meka.H1mekaRTXDriver"

if args.contains("--submit-activation") {
    let delegate = H1mekaRTXHostDelegate()
    let queue = DispatchQueue(label: "dev.h1meka.H1mekaRTXHost.activation")
    let request = OSSystemExtensionRequest.activationRequest(forExtensionWithIdentifier: extensionID, queue: queue)
    request.delegate = delegate
    print("H1MEKARTX_HOST_EVENT=submit_activation_request")
    OSSystemExtensionManager.shared.submitRequest(request)
    RunLoop.current.run(until: Date(timeIntervalSinceNow: 180))
} else {
    print("H1MEKARTX_HOST_EVENT=default_no_activation")
    print("H1MEKARTX_HOST_SAFETY=provider_open_false_ioserviceopen_false_bar_false_gpu_command_false")
}
