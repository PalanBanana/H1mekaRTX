// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "H1mekaMetalValidation",
    platforms: [
        .macOS(.v13)
    ],
    targets: [
        .executableTarget(
            name: "H1mekaMetalValidation",
            resources: [
                .process("Shaders")
            ]
        )
    ]
)
