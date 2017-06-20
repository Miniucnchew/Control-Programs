import Adafruit_ADS1x15 as ads
import Adafruit_MCP4725 as mcp
import time

# Initialize ADC and DAC i2c connection
dac = mcp.MCP4725(address=0x62)
adc = ads.ADS1015()

GAIN=1 #Gain for ADC

adc.start_adc(0, gain=GAIN)
try:
    while True:
        value = adc.get_last_result()

        if value%31 == 0:
            Vout = 2500
        else:
            Vout=1500

        dac.set_voltage(Vout)
        print('Position Measurement: {0:>4} | Signal Out: {1:>4} |'.format(value,Vout))


except:
    adc.stop_adc()
    dac.set_voltage(2048)
