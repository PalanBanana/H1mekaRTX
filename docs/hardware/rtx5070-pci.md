# RTX 5070 PCI Identification

Source dump: `dumps/rtx5070-gigabyte-windforce-oc-12g/`

## Device identity

| Field | Value |
|---|---|
| PCI address | `01:00.0` |
| Vendor ID | `0x10de` |
| Device ID | `0x2f04` |
| Revision ID | `0xa1` |
| Class | `0x030000` / VGA controller |
| Subsystem Vendor ID | `0x1458` |
| Subsystem Device ID | `0x417e` |
| IRQ | `167` |
| IOMMU group | `10` |

## lspci identity line

```text
01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GB205 [GeForce RTX 5070] [10de:2f04] (rev a1) (prog-if 00 [VGA controller])
	Subsystem: Gigabyte Technology Co., Ltd Device [1458:417e]
```

## DriverKit matching constants

```cpp
constexpr uint16_t kNvidiaVendorId = 0x10de;
constexpr uint16_t kRTX5070DeviceId = 0x2f04;
constexpr uint16_t kGigabyteSubsystemVendorId = 0x1458;
constexpr uint16_t kGigabyteRTX5070SubsystemDeviceId = 0x417e;
constexpr uint8_t  kRTX5070RevisionId = 0xa1;
constexpr uint32_t kVgaClassCode = 0x030000;
```
