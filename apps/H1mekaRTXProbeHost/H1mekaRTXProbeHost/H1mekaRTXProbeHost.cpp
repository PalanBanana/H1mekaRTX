//
//  H1mekaRTXProbeHost.cpp
//  H1mekaRTXProbeHost
//
//  Read-only PCI visibility probe for NVIDIA RTX 5070.
//

#include <os/log.h>

#include <DriverKit/IOUserServer.h>
#include <DriverKit/IOLib.h>
#include <PCIDriverKit/PCIDriverKit.h>

#include "H1mekaRTXProbeHost.h"

kern_return_t
IMPL(H1mekaRTXProbeHost, Start)
{
    kern_return_t ret = Start(provider, SUPERDISPATCH);

    os_log(OS_LOG_DEFAULT, "[H1mekaRTXProbe] Start called");

    if (ret != kIOReturnSuccess) {
        os_log(OS_LOG_DEFAULT, "[H1mekaRTXProbe] SUPERDISPATCH Start failed: 0x%x", ret);
        return ret;
    }

    IOPCIDevice *pciDevice = OSDynamicCast(IOPCIDevice, provider);
    if (pciDevice == nullptr) {
        os_log(OS_LOG_DEFAULT, "[H1mekaRTXProbe] Provider is not IOPCIDevice");
        return ret;
    }

    kern_return_t openRet = pciDevice->Open(this, 0);
    if (openRet != kIOReturnSuccess) {
        os_log(OS_LOG_DEFAULT, "[H1mekaRTXProbe] IOPCIDevice Open failed: 0x%x", openRet);
        return ret;
    }

    uint8_t bus = 0;
    uint8_t device = 0;
    uint8_t function = 0;

    uint16_t vendorID = 0;
    uint16_t deviceID = 0;
    uint16_t subsystemVendorID = 0;
    uint16_t subsystemID = 0;
    uint8_t revisionID = 0;

    pciDevice->GetBusDeviceFunction(&bus, &device, &function);

    pciDevice->ConfigurationRead16(kIOPCIConfigurationOffsetVendorID, &vendorID);
    pciDevice->ConfigurationRead16(kIOPCIConfigurationOffsetDeviceID, &deviceID);
    pciDevice->ConfigurationRead16(kIOPCIConfigurationOffsetSubSystemVendorID, &subsystemVendorID);
    pciDevice->ConfigurationRead16(kIOPCIConfigurationOffsetSubSystemID, &subsystemID);
    pciDevice->ConfigurationRead8(kIOPCIConfigurationOffsetRevisionID, &revisionID);

    os_log(OS_LOG_DEFAULT,
           "[H1mekaRTXProbe] PCI BDF %u:%u.%u VID=0x%04x DID=0x%04x SVID=0x%04x SSID=0x%04x REV=0x%02x",
           bus,
           device,
           function,
           vendorID,
           deviceID,
           subsystemVendorID,
           subsystemID,
           revisionID);

    pciDevice->Close(this, 0);

    os_log(OS_LOG_DEFAULT, "[H1mekaRTXProbe] Read-only PCI probe finished");

    return ret;
}
