import Adafruit_ADS1x15 as ads
import Adafruit_MCP4725 as mcp
import math
import time

# Initialize ADC and DAC i2c connection
dac = mcp.MCP4725(address=0x62)
adc = ads.ADS1015()

GAIN=1 #Gain for ADC


def mean(l):
    return float(sum(l))/max(len(l),1)

dist_moving_avg = 750

#try:
while True:
    dist = [0]*10
            
    for i in range(10):
        pos = adc.read_adc_difference(1, gain=GAIN, data_rate=3300)
        force = adc.read_adc_difference(2, gain=GAIN, data_rate=3300)

        dist[i] = adc.read_adc_difference(3, gain=GAIN, data_rate=3300)
        if i == 9:
            dist_moving_avg = mean(dist) 
        
##            if force < 30:
##                pos=0
##                Vout=2000

        if (dist[i] - dist_moving_avg < 15) and (force < 20):
            pos = 0
            Vout = 2048
        else:
            #Vout = int(math.sin(10*math.pi*time.time())*2000+2000)
            Vout = int(math.sin(30*pos/279)*500+2000)
            
        dac.set_voltage(Vout)
        print('Position: {0:>4} | Force: {1:>4} | Distance: {2:>4} | Vout: {3:>4} |'.format(pos, force, dist [i], Vout))


#except:

#    dac.set_voltage(2048)
