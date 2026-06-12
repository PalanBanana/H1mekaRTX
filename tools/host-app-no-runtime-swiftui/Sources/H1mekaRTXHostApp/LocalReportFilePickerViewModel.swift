import Foundation

struct LocalReportFilePickerViewModel {
    let title: String
    let subtitle: String
    let allowedFileTypeLabel: String
    let selectedFileName: String
    let importStatus: String
    let importMessages: [String]

    static let sample = LocalReportFilePickerViewModel(
        title: "Local Report Picker",
        subtitle: "Select a local JSON status report for preview validation only.",
        allowedFileTypeLabel: "JSON only",
        selectedFileName: "No file selected",
        importStatus: "IDLE",
        importMessages: [
            "Local file selection only",
            "No driver runtime",
            "No provider transition",
            "No device ownership transition",
            "No hardware-path action"
        ]
    )
}
