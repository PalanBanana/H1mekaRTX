import SwiftUI

struct MetalInjectionGoalBannerView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("RTX 5070 Metal Injection Goal")
                .font(.headline)

            Text("Goal tracked: full Metal graphics acceleration research for RTX 5070.")
                .font(.subheadline)
                .foregroundStyle(.secondary)

            Text("Current runtime state: DISABLED. This host app screen is UI-only and does not start driver, provider, device, hardware-path, or Metal runtime work.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(14)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
}
