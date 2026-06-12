import Foundation

enum LocalStatusModelLoader {
    static func loadBundledSample() -> HostAppStatusModel {
        guard let url = Bundle.module.url(forResource: "sample-host-status", withExtension: "json") else {
            return .fallback
        }

        do {
            let data = try Data(contentsOf: url)
            return try JSONDecoder().decode(HostAppStatusModel.self, from: data)
        } catch {
            return .fallback
        }
    }
}
