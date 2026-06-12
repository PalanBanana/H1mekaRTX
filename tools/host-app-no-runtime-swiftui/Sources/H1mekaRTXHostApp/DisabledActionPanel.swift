import SwiftUI

struct DisabledActionPanel: View {
    let actions: [String]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Disabled Future Actions")
                .font(.headline)

            LazyVGrid(columns: [GridItem(.adaptive(minimum: 220), spacing: 10)], spacing: 10) {
                ForEach(actions, id: \.self) { action in
                    Button(action) {
                    }
                    .disabled(true)
                }
            }

            Text("These controls are visible placeholders only. They do not perform runtime, activation, provider, device, or hardware work.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(14)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
}
