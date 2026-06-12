import SwiftUI

struct ImportResultStoreActionView: View {
    @ObservedObject var store: LocalImportResultStore

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Local Store Actions")
                .font(.headline)

            HStack(spacing: 10) {
                Button("Record Sample Accepted") {
                    let model = HostAppStatusModel.fallback
                    let result = LocalStatusImportResult.accept(
                        model,
                        messages: [
                            "Sample accepted result was stored",
                            "This is local UI state only",
                            "RTX 5070 Metal runtime remains disabled"
                        ]
                    )
                    store.record(fileName: "sample-accepted-local.json", result: result)
                }

                Button("Record Sample Rejected") {
                    let result = LocalStatusImportResult.reject([
                        "Sample rejected result was stored",
                        "No runtime action was performed"
                    ])
                    store.record(fileName: "sample-rejected-local.json", result: result)
                }

                Button("Clear Local Store") {
                    store.reset()
                }
            }

            Text("These controls modify local UI state only. They do not install drivers, activate drivers, transition providers, request device ownership, open hardware paths, or start RTX 5070 Metal runtime.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(14)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
}
