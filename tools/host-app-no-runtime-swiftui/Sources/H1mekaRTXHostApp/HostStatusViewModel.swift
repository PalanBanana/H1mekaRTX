import Foundation

struct HostStatusViewModel {
    let projectStatus: String
    let providerMatchStatus: String
    let activationStatus: String
    let evidenceStatus: String
    let hardwareAccessStatus: String
    let targetSummary: String
    let disabledActions: [String]

    static let sample = HostStatusViewModel(
        projectStatus: "RESEARCH_ONLY",
        providerMatchStatus: "NO_GO",
        activationStatus: "NO_GO",
        evidenceStatus: "NEEDS_USER_EVIDENCE",
        hardwareAccessStatus: "BLOCKED",
        targetSummary: "Target: NVIDIA RTX 5070 / vendor 0x10de / device 0x2f04 / match 0x2f0410de",
        disabledActions: [
            "Activate Driver",
            "Deactivate Driver",
            "Install Driver Extension",
            "Attach Provider",
            "Request Device Ownership",
            "Probe PCI",
            "Map BAR",
            "Run Metal Workload On RTX 5070"
        ]
    )
}
