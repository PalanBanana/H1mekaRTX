import SwiftUI
import UniformTypeIdentifiers

struct LocalReportFilePickerView: View {
    let viewModel: LocalReportFilePickerViewModel
    @State private var isImporterPresented = false
    @State private var selectedFileName: String
    @State private var importStatus: String
    @State private var importMessages: [String]

    init(viewModel: LocalReportFilePickerViewModel) {
        self.viewModel = viewModel
        self._selectedFileName = State(initialValue: viewModel.selectedFileName)
        self._importStatus = State(initialValue: viewModel.importStatus)
        self._importMessages = State(initialValue: viewModel.importMessages)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(viewModel.title)
                        .font(.headline)

                    Text(viewModel.subtitle)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                Spacer()

                Text(viewModel.allowedFileTypeLabel)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(.quaternary)
                    .clipShape(Capsule())
            }

            HStack {
                Text("Selected")
                    .foregroundStyle(.secondary)

                Spacer()

                Text(selectedFileName)
                    .fontWeight(.semibold)
            }
            .font(.subheadline)

            HStack {
                Text("Import status")
                    .foregroundStyle(.secondary)

                Spacer()

                Text(importStatus)
                    .fontWeight(.semibold)
            }
            .font(.subheadline)

            Button("Choose Local JSON Report") {
                isImporterPresented = true
            }

            VStack(alignment: .leading, spacing: 4) {
                ForEach(importMessages, id: \.self) { message in
                    Text("• \(message)")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }

            Text("File picker only. Selected JSON is for local preview validation and does not start driver, provider, device, or hardware work.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(14)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
        .fileImporter(
            isPresented: $isImporterPresented,
            allowedContentTypes: [.json],
            allowsMultipleSelection: false
        ) { result in
            switch result {
            case .success(let urls):
                let url = urls.first
                selectedFileName = url?.lastPathComponent ?? "No file selected"
                importStatus = "SELECTED_LOCAL_FILE"
                importMessages = [
                    "Local JSON file selected",
                    "Preview validation can be run separately",
                    "No driver runtime was started"
                ]
            case .failure:
                selectedFileName = "No file selected"
                importStatus = "IMPORT_CANCELLED_OR_FAILED"
                importMessages = [
                    "Local JSON file was not selected",
                    "No runtime action was performed"
                ]
            }
        }
    }
}
