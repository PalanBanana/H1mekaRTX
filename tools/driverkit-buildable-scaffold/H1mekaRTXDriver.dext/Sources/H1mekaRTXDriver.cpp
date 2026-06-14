#include <DriverKit/IOService.h>

class H1mekaRTXDriver final : public IOService {
public:
    bool init() override;
    kern_return_t Start(IOService* provider) override;
    kern_return_t Stop(IOService* provider) override;
};

bool H1mekaRTXDriver::init() {
    return IOService::init();
}

kern_return_t H1mekaRTXDriver::Start(IOService* provider) {
    // Build-scope scaffold only.
    // No provider open, no BAR mapping, no MMIO mutation, no GPU command submission.
    return IOService::Start(provider);
}

kern_return_t H1mekaRTXDriver::Stop(IOService* provider) {
    return IOService::Stop(provider);
}
