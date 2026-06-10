import SwiftUI

struct ContentView: View {
    @StateObject private var activationManager = H1mekaRTXProbeActivationManager()

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("H1mekaRTXProbe Installer")
                .font(.title)
                .bold()

            Text("RTX 5070 DriverKit read-only PCI probe")
                .font(.headline)

            Divider()

            Text("Status")
                .font(.headline)

            Text(activationManager.statusText)
                .textSelection(.enabled)

            Text(activationManager.lastResult)
                .textSelection(.enabled)
                .font(.system(.body, design: .monospaced))

            Divider()

            HStack {
                Button("Request Activation") {
                    activationManager.requestActivation()
                }

                Button("Request Deactivation") {
                    activationManager.requestDeactivation()
                }
            }

            Text("This app does not attempt graphics acceleration, framebuffer support, Metal support, GSP initialization, display engine support, or MMIO writes.")
                .font(.footnote)
                .foregroundStyle(.secondary)
                .textSelection(.enabled)
        }
        .padding()
        .frame(minWidth: 560, minHeight: 360)
    }
}

#Preview {
    ContentView()
}
