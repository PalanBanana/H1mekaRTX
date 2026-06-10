import Foundation
import SystemExtensions

@MainActor
final class H1mekaRTXProbeActivationManager: NSObject, ObservableObject {
    @Published var statusText: String = "Idle"
    @Published var lastResult: String = "No activation request has been submitted."

    private let extensionIdentifier = "com.palanbanana.H1mekaRTXProbeHost"

    func requestActivation() {
        statusText = "Submitting activation request..."
        lastResult = "Requesting activation for \(extensionIdentifier)"

        let request = OSSystemExtensionRequest.activationRequest(
            forExtensionWithIdentifier: extensionIdentifier,
            queue: .main
        )

        request.delegate = self
        OSSystemExtensionManager.shared.submitRequest(request)
    }

    func requestDeactivation() {
        statusText = "Submitting deactivation request..."
        lastResult = "Requesting deactivation for \(extensionIdentifier)"

        let request = OSSystemExtensionRequest.deactivationRequest(
            forExtensionWithIdentifier: extensionIdentifier,
            queue: .main
        )

        request.delegate = self
        OSSystemExtensionManager.shared.submitRequest(request)
    }
}

extension H1mekaRTXProbeActivationManager: OSSystemExtensionRequestDelegate {
    nonisolated func request(
        _ request: OSSystemExtensionRequest,
        didFinishWithResult result: OSSystemExtensionRequest.Result
    ) {
        Task { @MainActor in
            self.statusText = "Request finished"
            self.lastResult = "Result: \(result.rawValue)"
        }
    }

    nonisolated func request(
        _ request: OSSystemExtensionRequest,
        didFailWithError error: Error
    ) {
        Task { @MainActor in
            self.statusText = "Request failed"
            self.lastResult = error.localizedDescription
        }
    }

    nonisolated func requestNeedsUserApproval(_ request: OSSystemExtensionRequest) {
        Task { @MainActor in
            self.statusText = "User approval required"
            self.lastResult = "Open System Settings and approve the system extension if prompted."
        }
    }

    nonisolated func request(
        _ request: OSSystemExtensionRequest,
        actionForReplacingExtension existing: OSSystemExtensionProperties,
        withExtension replacement: OSSystemExtensionProperties
    ) -> OSSystemExtensionRequest.ReplacementAction {
        return .replace
    }
}
