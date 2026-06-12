import SwiftUI

struct ContentView: View {
    private let viewModel = HostStatusViewModel.sample
    private let importStore = LocalImportResultStore.sample

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    HeaderView(viewModel: viewModel)

                    MetalInjectionGoalBannerView()

                    HostAppLayoutSectionHeader(
                        title: "Status",
                        subtitle: "Local status summary and research boundary state."
                    )

                    StatusCardView(
                        title: "Project",
                        value: viewModel.projectStatus,
                        detail: "Research-only host-app shell"
                    )

                    StatusCardView(
                        title: "Provider Match",
                        value: viewModel.providerMatchStatus,
                        detail: "Provider transition remains gated"
                    )

                    StatusCardView(
                        title: "Activation",
                        value: viewModel.activationStatus,
                        detail: "Runtime actions remain disabled"
                    )

                    StatusCardView(
                        title: "Evidence",
                        value: viewModel.evidenceStatus,
                        detail: "User-provided evidence still required"
                    )

                    StatusCardView(
                        title: "Hardware",
                        value: viewModel.hardwareAccessStatus,
                        detail: "Hardware-path actions remain blocked"
                    )

                    HostAppLayoutSectionHeader(
                        title: "Local Import",
                        subtitle: "Local JSON preview, picker, and result-store UI."
                    )

                    ImportPreviewView(viewModel: .sample)

                    LocalReportFilePickerView(viewModel: .sample)

                    ImportResultStoreView(store: importStore)

                    ImportResultStoreActionView(store: importStore)

                    HostAppLayoutSectionHeader(
                        title: "Runtime Boundary",
                        subtitle: "Current no-runtime safety summary."
                    )

                    RuntimeBoundarySummaryView()

                    DisabledActionPanel(actions: viewModel.disabledActions)
                }
                .padding(20)
                .frame(maxWidth: 980, alignment: .leading)
            }
            .navigationTitle("H1mekaRTX Host")
        }
    }
}
