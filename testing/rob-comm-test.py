from smbus2 import SMBus, i2c_msg
import sys

I2C_CHANNEL = 12
LEGACY_I2C_CHANNEL = 4
ROB_ADDR = 0x1F
ACTUATORS_SIZE = 20
SENSORS_SIZE = 47

try:
	bus = SMBus(I2C_CHANNEL)
except:
	try:
		bus = SMBus(LEGACY_I2C_CHANNEL)
	except:
		sys.exit(1)

actuators_data = bytearray([0] * ACTUATORS_SIZE)
sensors_data = bytearray([0] * SENSORS_SIZE)
actuators_data[4] = 3

try:
	write = i2c_msg.write(ROB_ADDR, actuators_data)
	read = i2c_msg.read(ROB_ADDR, SENSORS_SIZE)
	bus.i2c_rdwr(write, read)
	sensors_data = list(read)
	#print(str(len(sensors_data)))
	#print(sensors_data)
except:
	sys.exit(1)


if len(sensors_data) < 0:
	sys.exit(1)
	
#print("sel = " + str(sensors_data[24]))
if (sensors_data[40]&0x0F) != 10:
	sys.exit(2)

sys.exit(0)