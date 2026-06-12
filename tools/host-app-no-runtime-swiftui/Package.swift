// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "H1mekaRTXHostApp",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .executable(
            name: "H1mekaRTXHostApp",
            targets: ["H1mekaRTXHostApp"]
        )
    ],
    targets: [
        .executableTarget(
            name: "H1mekaRTXHostApp"
        )
    ]
)
