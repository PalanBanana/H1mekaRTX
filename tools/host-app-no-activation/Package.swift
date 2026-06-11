// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "H1mekaRTXHostNoActivation",
    platforms: [
        .macOS(.v13)
    ],
    targets: [
        .executableTarget(
            name: "H1mekaRTXHostNoActivation"
        )
    ]
)
