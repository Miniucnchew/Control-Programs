import struct
import binhex

file = open("/dev/input/by-id/usb-2.4G_2.4G_Wireless_Device-if01-event-mouse", "rb") 
while True:
    byte = file.read(16)
    h = " ".join("{:02x}".format(ord(c)) for c in byte)
    print("byte=",h) 
    #byte.decode("utf-64")
    (type,code,value)=struct.unpack_from('hhi',byte,offset=8)
    print(["type=",type,"code=",code,"value=",value])
    
    if type == 1 and value == 1:
        if code == 272:
            print("LEFT PRESS")
        if code == 273:
            print("RIGHT PRESS")

    if type == 2:
        if code == 0:
            print("MOVE L/R",value)
        if code == 1:
            print("MOVE U/D",value)