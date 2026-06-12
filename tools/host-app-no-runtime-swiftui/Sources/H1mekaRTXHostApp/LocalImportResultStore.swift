import Combine
import Foundation

final class LocalImportResultStore: ObservableObject {
    @Published private(set) var latestStatus: String
    @Published private(set) var latestFileName: String
    @Published private(set) var latestMessages: [String]
    @Published private(set) var acceptedCount: Int
    @Published private(set) var rejectedCount: Int

    init(
        latestStatus: String = "NO_IMPORT_RESULT",
        latestFileName: String = "No file selected",
        latestMessages: [String] = [
            "No local import result has been stored yet",
            "Store is local UI state only",
            "No driver runtime action is available"
        ],
        acceptedCount: Int = 0,
        rejectedCount: Int = 0
    ) {
        self.latestStatus = latestStatus
        self.latestFileName = latestFileName
        self.latestMessages = latestMessages
        self.acceptedCount = acceptedCount
        self.rejectedCount = rejectedCount
    }

    func record(fileName: String, result: LocalStatusImportResult) {
        latestFileName = fileName
        latestStatus = result.accepted ? "ACCEPTED_LOCAL_IMPORT" : "REJECTED_LOCAL_IMPORT"
        latestMessages = result.messages

        if result.accepted {
            acceptedCount += 1
        } else {
            rejectedCount += 1
        }
    }

    func recordSelectionOnly(fileName: String) {
        latestFileName = fileName
        latestStatus = "SELECTED_LOCAL_FILE"
        latestMessages = [
            "Local JSON file was selected",
            "Validation result can be stored after decode",
            "No driver runtime action was performed"
        ]
    }

    func reset() {
        latestStatus = "NO_IMPORT_RESULT"
        latestFileName = "No file selected"
        latestMessages = [
            "Local import result store was reset",
            "Store remains local UI state only",
            "No runtime action was performed"
        ]
        acceptedCount = 0
        rejectedCount = 0
    }

    static let sample = LocalImportResultStore(
        latestStatus: "SAMPLE_IMPORTED_RESULT",
        latestFileName: "sample-imported-host-status.json",
        latestMessages: [
            "Sample local import accepted",
            "Status source remains local",
            "RTX 5070 Metal runtime remains disabled"
        ],
        acceptedCount: 1,
        rejectedCount: 0
    )
}
