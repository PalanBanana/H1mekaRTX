import Foundation

struct ImportPreviewViewModel {
    let title: String
    let accepted: Bool
    let messages: [String]
    let previewRows: [ImportPreviewRow]

    static let sample: ImportPreviewViewModel = {
        guard let url = Bundle.module.url(forResource: "sample-imported-host-status", withExtension: "json"),
              let data = try? Data(contentsOf: url) else {
            return ImportPreviewViewModel(
                title: "Local Import Preview",
                accepted: false,
                messages: ["Bundled sample import file was not found"],
                previewRows: []
            )
        }

        let result = LocalStatusImportValidator.validate(data: data)
        let model = result.model

        return ImportPreviewViewModel(
            title: "Local Import Preview",
            accepted: result.accepted,
            messages: result.messages,
            previewRows: [
                ImportPreviewRow(label: "Project", value: model?.projectStatus ?? "Unavailable"),
                ImportPreviewRow(label: "Provider", value: model?.providerMatchStatus ?? "Unavailable"),
                ImportPreviewRow(label: "Activation", value: model?.activationStatus ?? "Unavailable"),
                ImportPreviewRow(label: "Evidence", value: model?.evidenceStatus ?? "Unavailable"),
                ImportPreviewRow(label: "Hardware", value: model?.hardwareAccessStatus ?? "Unavailable"),
                ImportPreviewRow(label: "Source", value: model?.statusSource ?? "Unavailable")
            ]
        )
    }()
}

struct ImportPreviewRow: Identifiable, Equatable {
    let id = UUID()
    let label: String
    let value: String
}
