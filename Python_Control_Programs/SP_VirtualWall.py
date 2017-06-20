import Adafruit_ADS1x15 as ads
import Adafruit_MCP4725 as mcp
import math

# Initialize ADC and DAC i2c connection
dac = mcp.MCP4725(address=0x62)
adc = ads.ADS1015()

GAIN=1 #Gain for ADC

#y = [math.sin(z/16)*2000+2000 for z in range(0,100)]

# Main Loop

print('Reading ADS1x15 values, press Ctrl-C to quit...')

while True:
	values = [0]*3 #values[0]=position values[1]=force
	
	for i in [1,2,3]:

		values[i-1] = adc.read_adc_difference(i, gain=GAIN, data_rate=3300)

	if values[1]<40:
		values[0] = 0
	else:
		pass

	print('Pos: {0:0>4} {0:0>12b} | Force: {1:0>4} {1:0>12b} | Distance: {2:0>4} |'.format(*values))


	# Control section
	
	
	Vout = 4000-values[1]*2

	dac.set_voltage(Vout)

