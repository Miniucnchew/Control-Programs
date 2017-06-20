from __future__ import print_function
import sys, time
import usb.core
import usb.util
import time

import Adafruit_MCP4725
import Adafruit_ADS1x15

# hexidecimal product and id numbers:
dev = usb.core.find(idVendor=0x0488, idProduct=0x0280)

# first endpoint
interface = 0
endpoint = dev[0][(0,0)][0]
# if the OS kernel already claimed the device, which is most likely true
# thanks to http://stackoverflow.com/questions/8218683/pyusb-cannot-set-configuration
if dev.is_kernel_driver_active(interface) is True:
    dev.detach_kernel_driver(interface)       # tell the kernel to detach
    usb.util.claim_interface(dev, interface)  # claim the device

# Formatting ms time into hour:minute:second time
def fmt(t):
        return time.strftime("%H:%M:%S",time.gmtime(t/1000)) + ',%03d' % (t%1000)




# Opening i2c connection to MCP4725 (DAC) 
dac1 = Adafruit_MCP4725.MCP4725(address=0x62)
dac2 = Adafruit_MCP4725.MCP4725(address=0x63)


# Initializing my variables
collected = 0
maxAttempts = 5000
X = 2048  # initial mouse XY position
Y = 2048
minX = X
minY = Y
maxX = X
maxY = Y
tStart = int(round(time.time() * 1000))  # units of milliseconds
print("msec,dX,dY,X,Y,rX,rY")  # header line for CSV file



while 1: #( collected<maxAttempts ) :
    try:
        data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
        msec = int(round(time.time() * 1000)) - tStart
        collected += 1
        dx = data[1] # mouse delta-X movement
        dy = data[2] # mouse delta-Y movement
        if (dx > 127):
          dx = dx-256
        if (dy > 127):
          dy = dy-256
        X = X + dx
        Y = Y - dy

        if (X >= 4095 or X <= 0):
            X = 2048
        if (Y >= 4095 or Y <= 0):
            Y = 2048

#        maxX = max(X,maxX)
#        maxY = max(Y,maxY)
#        minX = min(X,minX)
#        minY = min(Y,minY)
#        print(fmt(msec)+", [%03d,%03d] [%05d,%05d] [%04d,%04d] collected = %04d" % (dx,dy,X,Y,maxX-minX,maxY-minY, collected))


        print('Voltage at [X-DAC,Y-DAC] = [%0.3f,%0.3f]  ----   [X,Y] = [%04d,%04d]' % (5.0*X/4095, 5.0*Y/4095, X,Y))

        # DAC I2C Communication:
        dac1.set_voltage(X)
        dac2.set_voltage(Y)

        if dx==0 and dy==0:
                break

    except usb.core.USBError as e:
        data = None
        if e.args == ('Operation timed out',):
            continue

usb.util.release_interface(dev, interface)  # release the device
dev.attach_kernel_driver(interface)  # reattach the device to the OS kernel
gpio.cleanup()
