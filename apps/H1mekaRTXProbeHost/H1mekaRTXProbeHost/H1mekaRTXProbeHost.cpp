//
//  H1mekaRTXProbeHost.cpp
//  H1mekaRTXProbeHost
//
//  Created by 히메카 on 6/11/26.
//

#include <os/log.h>

#include <DriverKit/IOUserServer.h>
#include <DriverKit/IOLib.h>

#include "H1mekaRTXProbeHost.h"

kern_return_t
IMPL(H1mekaRTXProbeHost, Start)
{
    kern_return_t ret;
    ret = Start(provider, SUPERDISPATCH);
    os_log(OS_LOG_DEFAULT, "Hello World");
    return ret;
}
