import os
import sys

EPUCK_BATTERY_PATH = "/sys/bus/i2c/devices/11-0048/iio:device0/in_voltage0_raw"
EPUCK_BATTERY_PATH_LEGACY = "/sys/bus/i2c/drivers/ads1015/3-0048/in4_input"
AUX_BATTERY_PATH = "/sys/bus/i2c/devices/11-0048/iio:device0/in_voltage1_raw"
AUX_BATTERY_PATH_LEGACY = "/sys/bus/i2c/drivers/ads1015/3-0048/in5_input"
EPUCK_BATTERY_SCALE_PATH = "/sys/bus/i2c/devices/11-0048/iio:device0/in_voltage0_scale"
AUX_BATTERY_SCALE_PATH = "/sys/bus/i2c/devices/11-0048/iio:device0/in_voltage1_scale"
LEGACY_BATTERY_SCALE = 1.0
BATTERY_MIN_VOLTAGE = 3.3
BATTERY_MAX_VOLTAGE = 4.138
BATTERY_VOLTAGE_RANGE = BATTERY_MAX_VOLTAGE - BATTERY_MIN_VOLTAGE

epuck_battery_path = ""
aux_battery_path = ""
epuck_scale_path = ""
aux_scale_path = ""
scale = 0.0
voltage = 0.0
raw_value = 0
percentage = 0.0

# Determine actual path to use for ADC driver (try iio, then hwmon)
if os.path.exists(EPUCK_BATTERY_PATH):
	epuck_battery_path = EPUCK_BATTERY_PATH
	aux_battery_path = AUX_BATTERY_PATH
	epuck_scale_path = EPUCK_BATTERY_SCALE_PATH
	aux_scale_path = AUX_BATTERY_SCALE_PATH
elif os.path.exists(EPUCK_BATTERY_PATH_LEGACY):
	epuck_battery_path = EPUCK_BATTERY_PATH_LEGACY
	aux_battery_path = AUX_BATTERY_PATH_LEGACY
	epuck_scale_path = None
	aux_scale_path = None
else:
	print("Cannot read ADC path")
	sys.exit(1)

# Read e-puck battery
if epuck_scale_path is not None:
	with open(epuck_scale_path, "r") as scale_file:
		scale = float(scale_file.read())	
else:
	scale = LEGACY_BATTERY_SCALE
	
with open(epuck_battery_path, "r") as battery_file:
	raw_value = float(battery_file.read())
	voltage = round((raw_value * scale) / 500.0, 2)
		
percentage = round((voltage - BATTERY_MIN_VOLTAGE) / BATTERY_VOLTAGE_RANGE * 100.0, 2)
if percentage < 0.0:
	percentage = 0.0
elif percentage > 100.0:
	percentage = 100.0

print("e-puck battery: " + str(voltage) + "V, " + str(percentage) + "% (" + str(raw_value) + ")")


# Read external battery
if aux_scale_path is not None:
	with open(aux_scale_path, "r") as scale_file:
		scale = float(scale_file.read())	
else:
	scale = LEGACY_BATTERY_SCALE

with open(aux_battery_path, "r") as battery_file:
	raw_value = float(battery_file.read())
	voltage = round((raw_value * scale) / 500.0, 2)	

percentage = round((voltage - BATTERY_MIN_VOLTAGE) / BATTERY_VOLTAGE_RANGE * 100.0, 2)
if percentage < 0.0:
	percentage = 0.0
elif percentage > 100.0:
	percentage = 100.0	
	
print("ext. battery: " + str(voltage) + "V, " + str(percentage) + "% (" + str(raw_value) + ")")
