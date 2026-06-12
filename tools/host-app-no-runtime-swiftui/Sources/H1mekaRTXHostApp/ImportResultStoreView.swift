import SwiftUI

struct ImportResultStoreView: View {
    @ObservedObject var store: LocalImportResultStore

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Local Import Result Store")
                        .font(.headline)

                    Text("Stores local preview/import results for UI display only.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                Spacer()

                Text(store.latestStatus)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(.quaternary)
                    .clipShape(Capsule())
            }

            HStack {
                Text("Latest file")
                    .foregroundStyle(.secondary)

                Spacer()

                Text(store.latestFileName)
                    .fontWeight(.semibold)
            }
            .font(.subheadline)

            HStack {
                Text("Accepted")
                    .foregroundStyle(.secondary)

                Spacer()

                Text("\(store.acceptedCount)")
                    .fontWeight(.semibold)
            }
            .font(.subheadline)

            HStack {
                Text("Rejected")
                    .foregroundStyle(.secondary)

                Spacer()

                Text("\(store.rejectedCount)")
                    .fontWeight(.semibold)
            }
            .font(.subheadline)

            VStack(alignment: .leading, spacing: 4) {
                ForEach(store.latestMessages, id: \.self) { message in
                    Text("• \(message)")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }

            Text("Store only. No driver installation, driver activation, provider transition, device ownership transition, hardware-path action, or RTX 5070 Metal runtime is performed.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(14)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
}
