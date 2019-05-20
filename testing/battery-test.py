
import Adafruit_ADS1x15
import sys

try:
	adc = Adafruit_ADS1x15.ADS1015(address=0x48, busnum=3)
except:
	sys.exit(1)

try:
	bat_ext = adc.read_adc(1, gain=1) # Range is +/- 4.096V.
except:
	sys.exit(1)
	
#print(str(bat_ext))
if bat_ext >= 950:
	sys.exit(0)
else:
	sys.exit(2)

    