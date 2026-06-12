import SwiftUI

struct ImportPreviewView: View {
    let viewModel: ImportPreviewViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(viewModel.title)
                    .font(.headline)

                Spacer()

                Text(viewModel.accepted ? "ACCEPTED" : "REJECTED")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(.quaternary)
                    .clipShape(Capsule())
            }

            ForEach(viewModel.previewRows) { row in
                HStack {
                    Text(row.label)
                        .foregroundStyle(.secondary)

                    Spacer()

                    Text(row.value)
                        .fontWeight(.semibold)
                }
                .font(.subheadline)
            }

            VStack(alignment: .leading, spacing: 4) {
                ForEach(viewModel.messages, id: \.self) { message in
                    Text("• \(message)")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }

            Text("Preview only. No driver runtime, provider transition, device ownership transition, or hardware-path action is performed.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(14)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
}
