import Foundation

struct LocalStatusImportPolicy {
    let allowedSchema: String
    let allowedStatusSources: Set<String>
    let allowedProjectStatuses: Set<String>
    let allowedProviderStatuses: Set<String>
    let allowedActivationStatuses: Set<String>
    let allowedEvidenceStatuses: Set<String>
    let allowedHardwareStatuses: Set<String>

    static let strict = LocalStatusImportPolicy(
        allowedSchema: "h1mekartx.host_app_status_model.v1",
        allowedStatusSources: [
            "LOCAL_BUNDLED_SAMPLE_ONLY",
            "LOCAL_IMPORTED_REPORT_ONLY",
            "LOCAL_FALLBACK_ONLY"
        ],
        allowedProjectStatuses: [
            "RESEARCH_ONLY"
        ],
        allowedProviderStatuses: [
            "NO_GO"
        ],
        allowedActivationStatuses: [
            "NO_GO"
        ],
        allowedEvidenceStatuses: [
            "NEEDS_USER_EVIDENCE"
        ],
        allowedHardwareStatuses: [
            "BLOCKED"
        ]
    )
}
