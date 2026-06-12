import SwiftUI

struct RuntimeBoundarySummaryView: View {
    private let rows: [RuntimeBoundaryRow] = [
        RuntimeBoundaryRow(label: "Driver runtime", value: "DISABLED"),
        RuntimeBoundaryRow(label: "Driver installation", value: "DISABLED"),
        RuntimeBoundaryRow(label: "Driver activation", value: "DISABLED"),
        RuntimeBoundaryRow(label: "Provider transition", value: "DISABLED"),
        RuntimeBoundaryRow(label: "Device ownership transition", value: "DISABLED"),
        RuntimeBoundaryRow(label: "Hardware-path actions", value: "DISABLED"),
        RuntimeBoundaryRow(label: "RTX 5070 Metal runtime", value: "DISABLED")
    ]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Runtime Boundary")
                .font(.headline)

            ForEach(rows) { row in
                HStack {
                    Text(row.label)
                        .foregroundStyle(.secondary)

                    Spacer()

                    Text(row.value)
                        .fontWeight(.semibold)
                }
                .font(.subheadline)
            }

            Text("Boundary summary only. No runtime request or hardware action is performed.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(14)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
}

struct RuntimeBoundaryRow: Identifiable, Equatable {
    let id = UUID()
    let label: String
    let value: String
}
