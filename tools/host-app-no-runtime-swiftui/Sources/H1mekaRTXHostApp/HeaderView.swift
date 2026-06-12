import SwiftUI

struct HeaderView: View {
    let viewModel: HostStatusViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("H1mekaRTX Host App")
                .font(.largeTitle)
                .fontWeight(.bold)

            Text("SwiftUI no-runtime skeleton")
                .font(.title3)
                .foregroundStyle(.secondary)

            Text(viewModel.targetSummary)
                .font(.callout)
                .foregroundStyle(.secondary)

            Text("Status source: \(viewModel.statusSource)")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }
}
