import Foundation

#if canImport(Metal)
import Metal

enum H1mekaMetalValidationError: Error, CustomStringConvertible {
    case noDefaultMetalDevice
    case noCommandQueue
    case missingShaderLibrary
    case missingFunction(String)
    case pipelineCreationFailed(String)
    case bufferCreationFailed(String)
    case commandBufferCreationFailed
    case encoderCreationFailed
    case verificationFailed(index: Int, expected: Float, actual: Float)

    var description: String {
        switch self {
        case .noDefaultMetalDevice:
            return "No default system Metal device is available."
        case .noCommandQueue:
            return "Failed to create a Metal command queue."
        case .missingShaderLibrary:
            return "Failed to load the default Metal shader library."
        case .missingFunction(let name):
            return "Missing Metal function: \(name)"
        case .pipelineCreationFailed(let reason):
            return "Failed to create compute pipeline: \(reason)"
        case .bufferCreationFailed(let name):
            return "Failed to create buffer: \(name)"
        case .commandBufferCreationFailed:
            return "Failed to create command buffer."
        case .encoderCreationFailed:
            return "Failed to create compute command encoder."
        case .verificationFailed(let index, let expected, let actual):
            return "Verification failed at index \(index): expected \(expected), actual \(actual)"
        }
    }
}

struct H1mekaMetalValidationReport: Codable {
    let schema: String
    let deviceName: String
    let registryID: UInt64
    let vectorLength: Int
    let validationPassed: Bool
    let safetyBoundary: SafetyBoundary

    struct SafetyBoundary: Codable {
        let usesExistingSystemMetalDeviceOnly: Bool
        let rtx5070MetalAccelerationAttempt: Bool
        let performsPCIConfigReads: Bool
        let performsPCIConfigWrites: Bool
        let performsMMIOReads: Bool
        let performsMMIOWrites: Bool
        let mapsBARMemory: Bool
        let barPoking: Bool
        let gpuReset: Bool
        let firmwareLoading: Bool
        let gspInitialization: Bool
        let displayEngineInit: Bool
        let framebufferInit: Bool
        let driverkitActivation: Bool
    }
}

func makeBuffer(device: MTLDevice, values: [Float], label: String) throws -> MTLBuffer {
    let byteCount = values.count * MemoryLayout<Float>.stride
    guard let buffer = device.makeBuffer(bytes: values, length: byteCount, options: [.storageModeShared]) else {
        throw H1mekaMetalValidationError.bufferCreationFailed(label)
    }
    buffer.label = label
    return buffer
}

func makeEmptyBuffer(device: MTLDevice, count: Int, label: String) throws -> MTLBuffer {
    let byteCount = count * MemoryLayout<Float>.stride
    guard let buffer = device.makeBuffer(length: byteCount, options: [.storageModeShared]) else {
        throw H1mekaMetalValidationError.bufferCreationFailed(label)
    }
    buffer.label = label
    return buffer
}

func runValidation() throws -> H1mekaMetalValidationReport {
    guard let device = MTLCreateSystemDefaultDevice() else {
        throw H1mekaMetalValidationError.noDefaultMetalDevice
    }

    guard let queue = device.makeCommandQueue() else {
        throw H1mekaMetalValidationError.noCommandQueue
    }
    queue.label = "H1mekaRTX validation command queue"

    guard let library = device.makeDefaultLibrary() else {
        throw H1mekaMetalValidationError.missingShaderLibrary
    }

    let functionName = "h1meka_vector_add"
    guard let function = library.makeFunction(name: functionName) else {
        throw H1mekaMetalValidationError.missingFunction(functionName)
    }

    let pipeline: MTLComputePipelineState
    do {
        pipeline = try device.makeComputePipelineState(function: function)
    } catch {
        throw H1mekaMetalValidationError.pipelineCreationFailed(String(describing: error))
    }

    let count = 256
    let a = (0..<count).map { Float($0) }
    let b = (0..<count).map { Float($0 * 2) }

    let aBuffer = try makeBuffer(device: device, values: a, label: "h1meka.input.a")
    let bBuffer = try makeBuffer(device: device, values: b, label: "h1meka.input.b")
    let outBuffer = try makeEmptyBuffer(device: device, count: count, label: "h1meka.output")

    guard let commandBuffer = queue.makeCommandBuffer() else {
        throw H1mekaMetalValidationError.commandBufferCreationFailed
    }
    commandBuffer.label = "H1mekaRTX validation command buffer"

    guard let encoder = commandBuffer.makeComputeCommandEncoder() else {
        throw H1mekaMetalValidationError.encoderCreationFailed
    }
    encoder.label = "H1mekaRTX validation compute encoder"
    encoder.setComputePipelineState(pipeline)
    encoder.setBuffer(aBuffer, offset: 0, index: 0)
    encoder.setBuffer(bBuffer, offset: 0, index: 1)
    encoder.setBuffer(outBuffer, offset: 0, index: 2)

    let threadsPerGrid = MTLSize(width: count, height: 1, depth: 1)
    let threadExecutionWidth = max(1, pipeline.threadExecutionWidth)
    let threadsPerThreadgroup = MTLSize(width: min(threadExecutionWidth, count), height: 1, depth: 1)

    encoder.dispatchThreads(threadsPerGrid, threadsPerThreadgroup: threadsPerThreadgroup)
    encoder.endEncoding()

    commandBuffer.commit()
    commandBuffer.waitUntilCompleted()

    let resultPointer = outBuffer.contents().bindMemory(to: Float.self, capacity: count)
    for index in 0..<count {
        let expected = a[index] + b[index]
        let actual = resultPointer[index]
        if abs(expected - actual) > 0.0001 {
            throw H1mekaMetalValidationError.verificationFailed(index: index, expected: expected, actual: actual)
        }
    }

    return H1mekaMetalValidationReport(
        schema: "h1mekartx.metal_validation_harness_runtime.v1",
        deviceName: device.name,
        registryID: device.registryID,
        vectorLength: count,
        validationPassed: true,
        safetyBoundary: .init(
            usesExistingSystemMetalDeviceOnly: true,
            rtx5070MetalAccelerationAttempt: false,
            performsPCIConfigReads: false,
            performsPCIConfigWrites: false,
            performsMMIOReads: false,
            performsMMIOWrites: false,
            mapsBARMemory: false,
            barPoking: false,
            gpuReset: false,
            firmwareLoading: false,
            gspInitialization: false,
            displayEngineInit: false,
            framebufferInit: false,
            driverkitActivation: false
        )
    )
}

do {
    let report = try runValidation()
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let data = try encoder.encode(report)
    if let json = String(data: data, encoding: .utf8) {
        print(json)
    }
} catch {
    fputs("H1mekaMetalValidation failed: \(error)\n", stderr)
    exit(1)
}

#else

fputs("Metal is not available on this platform.\n", stderr)
exit(1)

#endif
