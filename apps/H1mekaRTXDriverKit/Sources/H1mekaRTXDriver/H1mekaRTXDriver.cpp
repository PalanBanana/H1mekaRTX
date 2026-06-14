#include <DriverKit/IOService.h>
#include <DriverKit/IOLib.h>

class H1mekaRTXDriver final : public IOService
{
    OSDeclareDefaultStructors(H1mekaRTXDriver)

public:
    bool init() override;
    void free() override;
    kern_return_t Start(IOService* provider) override;
    kern_return_t Stop(IOService* provider) override;
};

#define super IOService
OSDefineMetaClassAndStructors(H1mekaRTXDriver, IOService)

bool H1mekaRTXDriver::init()
{
    return super::init();
}

void H1mekaRTXDriver::free()
{
    super::free();
}

kern_return_t H1mekaRTXDriver::Start(IOService* provider)
{
    // Phase 60M safety boundary:
    // - no provider open
    // - no IOServiceOpen
    // - no BAR mapping
    // - no BAR/MMIO mutation
    // - no PCI configuration writes
    // - no firmware load
    // - no GPU reset
    // - no framebuffer/display-engine init
    // - no GPU command submission
    return super::Start(provider);
}

kern_return_t H1mekaRTXDriver::Stop(IOService* provider)
{
    return super::Stop(provider);
}
