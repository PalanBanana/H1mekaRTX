#pragma once

#include <stdint.h>

namespace H1mekaRTX {

constexpr uint16_t kNvidiaVendorId = 0x10de;
constexpr uint16_t kRTX5070DeviceId = 0x2f04;
constexpr uint16_t kGigabyteSubsystemVendorId = 0x1458;
constexpr uint16_t kGigabyteRTX5070SubsystemDeviceId = 0x417e;
constexpr uint8_t  kRTX5070RevisionId = 0xa1;
constexpr uint32_t kVgaClassCode = 0x030000;

constexpr const char* kProjectName = "H1mekaRTX";
constexpr const char* kProbeName = "H1mekaRTXProbe";
constexpr const char* kTargetGpuName = "NVIDIA GB205 GeForce RTX 5070";

} // namespace H1mekaRTX
