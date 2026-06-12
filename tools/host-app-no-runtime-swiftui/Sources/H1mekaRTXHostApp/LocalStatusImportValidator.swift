import Foundation

struct LocalStatusImportResult: Equatable {
    let accepted: Bool
    let messages: [String]
    let model: HostAppStatusModel?

    static func reject(_ messages: [String]) -> LocalStatusImportResult {
        LocalStatusImportResult(accepted: false, messages: messages, model: nil)
    }

    static func accept(_ model: HostAppStatusModel, messages: [String]) -> LocalStatusImportResult {
        LocalStatusImportResult(accepted: true, messages: messages, model: model)
    }
}

enum LocalStatusImportValidator {
    static func validate(data: Data, policy: LocalStatusImportPolicy = .strict) -> LocalStatusImportResult {
        let model: HostAppStatusModel

        do {
            model = try JSONDecoder().decode(HostAppStatusModel.self, from: data)
        } catch {
            return .reject(["JSON decode failed"])
        }

        var failures: [String] = []

        if model.schema != policy.allowedSchema {
            failures.append("Unsupported schema")
        }

        if !policy.allowedStatusSources.contains(model.statusSource) {
            failures.append("Unsupported status source")
        }

        if !policy.allowedProjectStatuses.contains(model.projectStatus) {
            failures.append("Unsupported project status")
        }

        if !policy.allowedProviderStatuses.contains(model.providerMatchStatus) {
            failures.append("Unsupported provider status")
        }

        if !policy.allowedActivationStatuses.contains(model.activationStatus) {
            failures.append("Unsupported activation status")
        }

        if !policy.allowedEvidenceStatuses.contains(model.evidenceStatus) {
            failures.append("Unsupported evidence status")
        }

        if !policy.allowedHardwareStatuses.contains(model.hardwareAccessStatus) {
            failures.append("Unsupported hardware status")
        }

        if model.disabledActions.isEmpty {
            failures.append("Disabled action list is empty")
        }

        if failures.isEmpty {
            return .accept(model, messages: ["Local status import accepted"])
        }

        return .reject(failures)
    }
}
