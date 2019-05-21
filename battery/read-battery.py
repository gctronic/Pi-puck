#!/usr/bin/env python3

import Adafruit_ADS1x15
import time

# 12 bits resolution, range +/- 4.096V
# The ADC read half of the actual voltage thus multiply by 2 to get the correct value.
ADC_TO_VOLT = (4.096/2048)*2

adc = Adafruit_ADS1x15.ADS1015(address=0x48, busnum=3)

while 1:
	bat_epuck = adc.read_adc(0, gain=1) # Range is +/- 4.096V.
	bat_ext = adc.read_adc(1, gain=1) # Range is +/- 4.096V.
	print("e-puck: " + str(bat_epuck*ADC_TO_VOLT) + "V (" + str(bat_epuck) + "), ext: " + str(bat_ext*ADC_TO_VOLT) + "V (" + str(bat_ext) + ")")
	time.sleep(1)
    