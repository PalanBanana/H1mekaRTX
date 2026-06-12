import SwiftUI

@main
struct H1mekaRTXHostApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView(viewModel: HostStatusViewModel.sample)
        }
    }
}
