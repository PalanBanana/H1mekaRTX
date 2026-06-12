import SwiftUI

struct ContentView: View {
    let viewModel: HostStatusViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            HeaderView(viewModel: viewModel)

            StatusCardView(
                title: "Project",
                value: viewModel.projectStatus,
                detail: "Research-only host app skeleton"
            )

            StatusCardView(
                title: "Provider Match",
                value: viewModel.providerMatchStatus,
                detail: "Local report state only"
            )

            StatusCardView(
                title: "Activation",
                value: viewModel.activationStatus,
                detail: "No runtime path is enabled"
            )

            StatusCardView(
                title: "Evidence",
                value: viewModel.evidenceStatus,
                detail: "User-private evidence remains required"
            )

            StatusCardView(
                title: "Hardware Access",
                value: viewModel.hardwareAccessStatus,
                detail: "GPU hardware actions remain blocked"
            )

            ImportPreviewView(viewModel: .sample)

            LocalReportFilePickerView(viewModel: .sample)

            DisabledActionPanel(actions: viewModel.disabledActions)

            Spacer()
        }
        .padding(24)
        .frame(minWidth: 760, minHeight: 620)
    }
}
