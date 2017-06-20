import Adafruit_ADS1x15 as ads

adc = ads.ADS1015()

GAIN=1

print('Reading ADS1x15 values, press Ctrl-C to quit...')

while True:
	values = [0]*3
	for i in [1,2,]:

		values[i-1] = adc.read_adc_difference(i, gain=GAIN, data_rate=3300)

	if values[1]<40:
		values[0] = 0
	else:
		pass

	print('Pos: {0:0>4} {0:0>12b} | Force: {1:0>4} {1:0>12b}'.format(*values))
