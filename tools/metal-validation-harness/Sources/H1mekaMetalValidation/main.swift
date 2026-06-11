import Foundation

#if canImport(Metal)
import Metal

enum H1mekaMetalValidationError: Error, CustomStringConvertible {
    case noDefaultMetalDevice
    case noCommandQueue
    case missingShaderSource
    case libraryCreationFailed(String)
    case missingFunction(String)
    case pipelineCreationFailed(String)
    case bufferCreationFailed(String)
    case commandBufferCreationFailed
    case encoderCreationFailed
    case verificationFailed(workload: String, index: Int, expected: Float, actual: Float)

    var description: String {
        switch self {
        case .noDefaultMetalDevice:
            return "No default system Metal device is available."
        case .noCommandQueue:
            return "Failed to create a Metal command queue."
        case .missingShaderSource:
            return "Failed to load reference_workloads.metal from package resources."
        case .libraryCreationFailed(let reason):
            return "Failed to create Metal shader library: \(reason)"
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
        case .verificationFailed(let workload, let index, let expected, let actual):
            return "Verification failed for \(workload) at index \(index): expected \(expected), actual \(actual)"
        }
    }
}

struct WorkloadResult: Codable {
    let name: String
    let functionName: String
    let vectorLength: Int
    let validationPassed: Bool
    let maxAbsoluteError: Float
}

struct H1mekaMetalValidationReport: Codable {
    let schema: String
    let deviceName: String
    let registryID: UInt64
    let workloadCount: Int
    let validationPassed: Bool
    let workloads: [WorkloadResult]
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
        let hardwareCommandSubmissionToRTX5070: Bool
        let resourceAllocationOnRTX5070: Bool
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

func makeScalarBuffer(device: MTLDevice, value: Float, label: String) throws -> MTLBuffer {
    var scalar = value
    guard let buffer = device.makeBuffer(bytes: &scalar, length: MemoryLayout<Float>.stride, options: [.storageModeShared]) else {
        throw H1mekaMetalValidationError.bufferCreationFailed(label)
    }
    buffer.label = label
    return buffer
}

func loadReferenceLibrary(device: MTLDevice) throws -> MTLLibrary {
    guard let url = Bundle.module.url(forResource: "reference_workloads", withExtension: "metal", subdirectory: "Shaders") else {
        throw H1mekaMetalValidationError.missingShaderSource
    }

    let source = try String(contentsOf: url, encoding: .utf8)

    do {
        return try device.makeLibrary(source: source, options: nil)
    } catch {
        throw H1mekaMetalValidationError.libraryCreationFailed(String(describing: error))
    }
}

func makePipeline(device: MTLDevice, library: MTLLibrary, functionName: String) throws -> MTLComputePipelineState {
    guard let function = library.makeFunction(name: functionName) else {
        throw H1mekaMetalValidationError.missingFunction(functionName)
    }

    do {
        return try device.makeComputePipelineState(function: function)
    } catch {
        throw H1mekaMetalValidationError.pipelineCreationFailed(String(describing: error))
    }
}

func submitAndVerify(
    workloadName: String,
    functionName: String,
    queue: MTLCommandQueue,
    pipeline: MTLComputePipelineState,
    buffers: [(MTLBuffer, Int)],
    count: Int,
    expected: [Float],
    outputBuffer: MTLBuffer
) throws -> WorkloadResult {
    guard let commandBuffer = queue.makeCommandBuffer() else {
        throw H1mekaMetalValidationError.commandBufferCreationFailed
    }
    commandBuffer.label = "H1mekaRTX reference workload: \(workloadName)"

    guard let encoder = commandBuffer.makeComputeCommandEncoder() else {
        throw H1mekaMetalValidationError.encoderCreationFailed
    }

    encoder.label = "H1mekaRTX reference encoder: \(workloadName)"
    encoder.setComputePipelineState(pipeline)

    for (buffer, index) in buffers {
        encoder.setBuffer(buffer, offset: 0, index: index)
    }

    let threadsPerGrid = MTLSize(width: count, height: 1, depth: 1)
    let width = max(1, min(pipeline.threadExecutionWidth, count))
    let threadsPerThreadgroup = MTLSize(width: width, height: 1, depth: 1)

    encoder.dispatchThreads(threadsPerGrid, threadsPerThreadgroup: threadsPerThreadgroup)
    encoder.endEncoding()

    commandBuffer.commit()
    commandBuffer.waitUntilCompleted()

    let resultPointer = outputBuffer.contents().bindMemory(to: Float.self, capacity: count)
    var maxError: Float = 0

    for index in 0..<count {
        let actual = resultPointer[index]
        let error = abs(expected[index] - actual)
        maxError = max(maxError, error)
        if error > 0.0001 {
            throw H1mekaMetalValidationError.verificationFailed(
                workload: workloadName,
                index: index,
                expected: expected[index],
                actual: actual
            )
        }
    }

    return WorkloadResult(
        name: workloadName,
        functionName: functionName,
        vectorLength: count,
        validationPassed: true,
        maxAbsoluteError: maxError
    )
}

func runValidationSuite() throws -> H1mekaMetalValidationReport {
    guard let device = MTLCreateSystemDefaultDevice() else {
        throw H1mekaMetalValidationError.noDefaultMetalDevice
    }

    guard let queue = device.makeCommandQueue() else {
        throw H1mekaMetalValidationError.noCommandQueue
    }
    queue.label = "H1mekaRTX reference workload command queue"

    let library = try loadReferenceLibrary(device: device)

    let count = 512
    let a = (0..<count).map { Float($0) * 0.25 }
    let b = (0..<count).map { Float($0 % 17) * 1.5 }
    let alpha: Float = 2.5
    let beta: Float = -0.75

    let vectorAddPipeline = try makePipeline(device: device, library: library, functionName: "h1meka_vector_add")
    let saxpyPipeline = try makePipeline(device: device, library: library, functionName: "h1meka_saxpy")
    let squarePipeline = try makePipeline(device: device, library: library, functionName: "h1meka_square")
    let vectorMultiplyPipeline = try makePipeline(device: device, library: library, functionName: "h1meka_vector_multiply")
    let vectorSubtractPipeline = try makePipeline(device: device, library: library, functionName: "h1meka_vector_subtract")
    let axpbyPipeline = try makePipeline(device: device, library: library, functionName: "h1meka_axpby")

    let aBuffer = try makeBuffer(device: device, values: a, label: "h1meka.reference.a")
    let bBuffer = try makeBuffer(device: device, values: b, label: "h1meka.reference.b")
    let alphaBuffer = try makeScalarBuffer(device: device, value: alpha, label: "h1meka.reference.alpha")
    let betaBuffer = try makeScalarBuffer(device: device, value: beta, label: "h1meka.reference.beta")

    let vectorAddOut = try makeEmptyBuffer(device: device, count: count, label: "h1meka.reference.vector_add.out")
    let saxpyOut = try makeEmptyBuffer(device: device, count: count, label: "h1meka.reference.saxpy.out")
    let squareOut = try makeEmptyBuffer(device: device, count: count, label: "h1meka.reference.square.out")
    let vectorMultiplyOut = try makeEmptyBuffer(device: device, count: count, label: "h1meka.reference.vector_multiply.out")
    let vectorSubtractOut = try makeEmptyBuffer(device: device, count: count, label: "h1meka.reference.vector_subtract.out")
    let axpbyOut = try makeEmptyBuffer(device: device, count: count, label: "h1meka.reference.axpby.out")

    let vectorAddExpected = zip(a, b).map { $0 + $1 }
    let saxpyExpected = zip(a, b).map { alpha * $0 + $1 }
    let squareExpected = a.map { $0 * $0 }
    let vectorMultiplyExpected = zip(a, b).map { $0 * $1 }
    let vectorSubtractExpected = zip(a, b).map { $0 - $1 }
    let axpbyExpected = zip(a, b).map { alpha * $0 + beta * $1 }

    let results = try [
        submitAndVerify(
            workloadName: "vector_add",
            functionName: "h1meka_vector_add",
            queue: queue,
            pipeline: vectorAddPipeline,
            buffers: [(aBuffer, 0), (bBuffer, 1), (vectorAddOut, 2)],
            count: count,
            expected: vectorAddExpected,
            outputBuffer: vectorAddOut
        ),
        submitAndVerify(
            workloadName: "saxpy",
            functionName: "h1meka_saxpy",
            queue: queue,
            pipeline: saxpyPipeline,
            buffers: [(aBuffer, 0), (bBuffer, 1), (alphaBuffer, 2), (saxpyOut, 3)],
            count: count,
            expected: saxpyExpected,
            outputBuffer: saxpyOut
        ),
        submitAndVerify(
            workloadName: "square",
            functionName: "h1meka_square",
            queue: queue,
            pipeline: squarePipeline,
            buffers: [(aBuffer, 0), (squareOut, 1)],
            count: count,
            expected: squareExpected,
            outputBuffer: squareOut
        ),
        submitAndVerify(
            workloadName: "vector_multiply",
            functionName: "h1meka_vector_multiply",
            queue: queue,
            pipeline: vectorMultiplyPipeline,
            buffers: [(aBuffer, 0), (bBuffer, 1), (vectorMultiplyOut, 2)],
            count: count,
            expected: vectorMultiplyExpected,
            outputBuffer: vectorMultiplyOut
        ),
        submitAndVerify(
            workloadName: "vector_subtract",
            functionName: "h1meka_vector_subtract",
            queue: queue,
            pipeline: vectorSubtractPipeline,
            buffers: [(aBuffer, 0), (bBuffer, 1), (vectorSubtractOut, 2)],
            count: count,
            expected: vectorSubtractExpected,
            outputBuffer: vectorSubtractOut
        ),
        submitAndVerify(
            workloadName: "axpby",
            functionName: "h1meka_axpby",
            queue: queue,
            pipeline: axpbyPipeline,
            buffers: [(aBuffer, 0), (bBuffer, 1), (alphaBuffer, 2), (betaBuffer, 3), (axpbyOut, 4)],
            count: count,
            expected: axpbyExpected,
            outputBuffer: axpbyOut
        ),
    ]

    return H1mekaMetalValidationReport(
        schema: "h1mekartx.metal_reference_workload_runtime.v1",
        deviceName: device.name,
        registryID: device.registryID,
        workloadCount: results.count,
        validationPassed: results.allSatisfy { $0.validationPassed },
        workloads: results,
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
            driverkitActivation: false,
            hardwareCommandSubmissionToRTX5070: false,
            resourceAllocationOnRTX5070: false
        )
    )
}

do {
    let report = try runValidationSuite()
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
