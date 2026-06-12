import Foundation

struct HostStatusViewModel {
    let projectStatus: String
    let providerMatchStatus: String
    let activationStatus: String
    let evidenceStatus: String
    let hardwareAccessStatus: String
    let statusSource: String
    let targetSummary: String
    let disabledActions: [String]

    init(model: HostAppStatusModel) {
        self.projectStatus = model.projectStatus
        self.providerMatchStatus = model.providerMatchStatus
        self.activationStatus = model.activationStatus
        self.evidenceStatus = model.evidenceStatus
        self.hardwareAccessStatus = model.hardwareAccessStatus
        self.statusSource = model.statusSource
        self.targetSummary = model.targetSummary
        self.disabledActions = model.disabledActions
    }

    static let sample = HostStatusViewModel(
        model: LocalStatusModelLoader.loadBundledSample()
    )
}
