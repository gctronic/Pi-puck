import os
import sys

AUX_BATTERY_PATH = "/sys/bus/i2c/devices/11-0048/iio:device0/in_voltage1_raw"
AUX_BATTERY_PATH_LEGACY = "/sys/bus/i2c/drivers/ads1015/3-0048/in5_input"
AUX_BATTERY_SCALE_PATH = "/sys/bus/i2c/devices/11-0048/iio:device0/in_voltage1_scale"
LEGACY_BATTERY_SCALE = 1.0

aux_battery_path = ""
aux_scale_path = ""
scale = 0.0
raw_value = 0

# Determine actual path to use for ADC driver (try iio, then hwmon)
if os.path.exists(AUX_BATTERY_PATH):
	aux_battery_path = AUX_BATTERY_PATH
	aux_scale_path = AUX_BATTERY_SCALE_PATH
elif os.path.exists(AUX_BATTERY_PATH_LEGACY):
	aux_battery_path = AUX_BATTERY_PATH_LEGACY
	aux_scale_path = None
else:
	sys.exit(1)

# Read external battery
try:
	if aux_scale_path is not None:
		with open(aux_scale_path, "r") as scale_file:
			scale = float(scale_file.read())	
	else:
		scale = LEGACY_BATTERY_SCALE

	with open(aux_battery_path, "r") as battery_file:
		raw_value = float(battery_file.read())
except:
	sys.exit(1)
	
#print(str(raw_value*scale))
if (raw_value*scale) >= 1900:
	sys.exit(0)
else:
	sys.exit(2)

    