from smbus2 import SMBus, i2c_msg
import sys
import time

I2C_CHANNEL = 12
LEGACY_I2C_CHANNEL = 4
GROUNDSENSOR_ADDRESS = 0x60  # Device address

groundData = bytearray([0] * 6)
groundValue = [0 for x in range(3)]
bus = None
	
def read_reg(reg, count):
	global bus
	global imu_addr
	data = None
	
	try:			
		data = bus.read_i2c_block_data(GROUNDSENSOR_ADDRESS, reg, count)
		#print(data)
	except:
		print("read error")
		return None

	return data;

try:
	bus = SMBus(I2C_CHANNEL)
except:
	try:
		bus = SMBus(LEGACY_I2C_CHANNEL)
	except:
		print("Cannot open I2C device")
		sys.exit(1)

while 1:

	start = time.time()

	groundData = read_reg(0, 6)

	groundValue[0] = (groundData[1] + (groundData[0]<<8))
	groundValue[1] = (groundData[3] + (groundData[2]<<8))
	groundValue[2] = (groundData[5] + (groundData[4]<<8))

	print("left={0:>3d}, center={1:>3d}, right={2:>3d}".format(groundValue[0], groundValue[1], groundValue[2]))

	# Communication frequency @ 20 Hz.
	time_diff = time.time() - start
	if time_diff < 0.050:
		time.sleep(0.050 - time_diff);
