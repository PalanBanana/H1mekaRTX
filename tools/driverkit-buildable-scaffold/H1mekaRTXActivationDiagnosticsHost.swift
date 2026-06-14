import Foundation
import SystemExtensions

final class Delegate: NSObject, OSSystemExtensionRequestDelegate {
    let semaphore = DispatchSemaphore(value: 0)
    var didFinish = false
    var didFail = false
    var needsUserApproval = false
    var replacementRequested = false
    var resultText = "none"
    var errorText = "none"

    func requestNeedsUserApproval(_ request: OSSystemExtensionRequest) {
        needsUserApproval = true
        print("H1MEKARTX_SYSEXT_EVENT=request_needs_user_approval")
        fflush(stdout)
    }

    func request(_ request: OSSystemExtensionRequest, didFinishWithResult result: OSSystemExtensionRequest.Result) {
        didFinish = true
        resultText = String(describing: result)
        print("H1MEKARTX_SYSEXT_EVENT=did_finish")
        print("H1MEKARTX_SYSEXT_RESULT=\(resultText)")
        fflush(stdout)
        semaphore.signal()
    }

    func request(_ request: OSSystemExtensionRequest, didFailWithError error: Error) {
        didFail = true
        let nsError = error as NSError
        errorText = "\(nsError.domain):\(nsError.code):\(nsError.localizedDescription)"
        print("H1MEKARTX_SYSEXT_EVENT=did_fail")
        print("H1MEKARTX_SYSEXT_ERROR_DOMAIN=\(nsError.domain)")
        print("H1MEKARTX_SYSEXT_ERROR_CODE=\(nsError.code)")
        print("H1MEKARTX_SYSEXT_ERROR_DESCRIPTION=\(nsError.localizedDescription)")
        fflush(stdout)
        semaphore.signal()
    }

    func request(_ request: OSSystemExtensionRequest, actionForReplacingExtension existing: OSSystemExtensionProperties, withExtension ext: OSSystemExtensionProperties) -> OSSystemExtensionRequest.ReplacementAction {
        replacementRequested = true
        print("H1MEKARTX_SYSEXT_EVENT=replacement_requested")
        fflush(stdout)
        return .replace
    }
}

func argValue(_ name: String, defaultValue: String) -> String {
    let args = CommandLine.arguments
    if let idx = args.firstIndex(of: name), idx + 1 < args.count {
        return args[idx + 1]
    }
    return defaultValue
}

let args = CommandLine.arguments
let submit = args.contains("--submit-activation")
let extensionID = argValue("--extension-id", defaultValue: "dev.h1meka.H1mekaRTXDriver")
let waitSeconds = Int(argValue("--wait-seconds", defaultValue: "180")) ?? 180

if !submit {
    print("H1MEKARTX_SYSEXT_EVENT=refuse_without_submit_activation")
    exit(2)
}

let queue = DispatchQueue(label: "dev.h1meka.H1mekaRTX.activation-diagnostics")
let delegate = Delegate()
let request = OSSystemExtensionRequest.activationRequest(forExtensionWithIdentifier: extensionID, queue: queue)
request.delegate = delegate

print("H1MEKARTX_SYSEXT_EVENT=submit_activation_request")
print("H1MEKARTX_SYSEXT_EXTENSION_ID=\(extensionID)")
fflush(stdout)

OSSystemExtensionManager.shared.submitRequest(request)

let timeout = DispatchTime.now() + .seconds(waitSeconds)
let waitResult = delegate.semaphore.wait(timeout: timeout)

if waitResult == .timedOut {
    print("H1MEKARTX_SYSEXT_EVENT=delegate_timeout")
    print("H1MEKARTX_SYSEXT_WAIT_SECONDS=\(waitSeconds)")
    fflush(stdout)
    exit(3)
}

print("H1MEKARTX_SYSEXT_EVENT=delegate_completed")
print("H1MEKARTX_SYSEXT_DID_FINISH=\(delegate.didFinish)")
print("H1MEKARTX_SYSEXT_DID_FAIL=\(delegate.didFail)")
print("H1MEKARTX_SYSEXT_NEEDS_USER_APPROVAL=\(delegate.needsUserApproval)")
print("H1MEKARTX_SYSEXT_REPLACEMENT_REQUESTED=\(delegate.replacementRequested)")
print("H1MEKARTX_SYSEXT_RESULT_TEXT=\(delegate.resultText)")
print("H1MEKARTX_SYSEXT_ERROR_TEXT=\(delegate.errorText)")
fflush(stdout)

if delegate.didFail {
    exit(4)
}
exit(0)
