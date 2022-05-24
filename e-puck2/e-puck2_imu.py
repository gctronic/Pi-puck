from smbus2 import SMBus, i2c_msg
import sys
import time
import struct

I2C_CHANNEL = 12
LEGACY_I2C_CHANNEL = 4
NUM_SAMPLES_CALIBRATION = 20
GRAVITY_MPU9250 = 16384 # To be defined...1 g for 16 bits accelerometer
AK8963_ADDRESS = 0x0C # Address of magnetometer
AK8963_XOUT_L = 0x03 # data
MPU9250_ADDRESS_AD1_0 = 0x68  # Device address when AD1 = 0
MPU9250_ADDRESS_AD1_1 = 0x69
INT_STATUS = 0x3A
ACCEL_XOUT_H = 0x3B
TEMP_OUT_H = 0x41
GYRO_XOUT_H = 0x43
GYRO_CONFIG = 0x1B
SMPLRT_DIV = 0x19

accData = bytearray([0] * 6)
gyroData = bytearray([0] * 6)
temperatureData = 0
accValue = [0 for x in range(3)]
accSum = [0 for x in range(3)]
accOffset = [0 for x in range(3)]
gyroValue = [0 for x in range(3)]
gyroSum = [0 for x in range(3)]
gyroOffset = [0 for x in range(3)]
imu_addr = MPU9250_ADDRESS_AD1_0
bus = None

# The chip has two alternative addresses based on the AD1 pin.
def mpu9250_change_addr():
	global imu_addr
	if(imu_addr == MPU9250_ADDRESS_AD1_0):
		imu_addr = MPU9250_ADDRESS_AD1_1
	else:
		imu_addr = MPU9250_ADDRESS_AD1_0

def write_reg(reg, data):
	global bus 
	global imu_addr
	trials = 0
	
	while trials < 2:
		try:
			bus.write_i2c_block_data(imu_addr, reg, data)
		except:
			trials += 1
			mpu9250_change_addr()
			continue
		break
		
	if trials == 2:
		print("write error")
		return -1
	
	return 0
		
def read_reg(reg, count):
	global bus
	global imu_addr
	trials = 0
	data = None
	
	while trials < 2:
		try:			
			data = bus.read_i2c_block_data(imu_addr, reg, count)
			#print(data)
		except:
			#print("trial = " + str(trials))
			trials += 1
			mpu9250_change_addr()
			continue
		break
	
	if trials == 2:
		print("read error")
		return None
	
	return data;
		
def calibrateAcc():
	samplesCount = 0
	# reset and send configuration first?
	for i in range(NUM_SAMPLES_CALIBRATION):
		accData = read_reg(ACCEL_XOUT_H, 6)
		if(accData != None):
			accSum[0] += struct.unpack("<h", struct.pack("<BB", accData[1], accData[0]))[0]
			accSum[1] += struct.unpack("<h", struct.pack("<BB", accData[3], accData[2]))[0]
			accSum[2] += struct.unpack("<h", struct.pack("<BB", accData[5], accData[4]))[0] - GRAVITY_MPU9250 #!!!
			samplesCount += 1
			#print("acc sums: x={0:>+6d}, y={1:>+6d}, z={2:>+6d} (samples={3:>3d})\n".format(accSum[0], accSum[1], accSum[2], samplesCount))
		time.sleep(0.050)
	accOffset[0] = int(accSum[0]/samplesCount)
	accOffset[1] = int(accSum[1]/samplesCount)
	accOffset[2] = int(accSum[2]/samplesCount)
	print("acc offsets: x={0:>+5d}, y={1:>+5d}, z={2:>+5d} (samples={3:>3d})\n".format(accOffset[0], accOffset[1], accOffset[2], samplesCount))

def calibrateGyro():
	samplesCount = 0
	# reset and send configuration first?
	for i in range(NUM_SAMPLES_CALIBRATION):
		gyroData = read_reg(GYRO_XOUT_H, 6)
		if(gyroData != None):
			gyroSum[0] += struct.unpack("<h", struct.pack("<BB", gyroData[1], gyroData[0]))[0]
			gyroSum[1] += struct.unpack("<h", struct.pack("<BB", gyroData[3], gyroData[2]))[0]
			gyroSum[2] += struct.unpack("<h", struct.pack("<BB", gyroData[5], gyroData[4]))[0]
			samplesCount += 1
			#print("gyro sums: x={0:>+6d}, y={1:>+6d}, z={2:>+6d} (samples={3:>3d})".format(gyroSum[0], gyroSum[1], gyroSum[2], samplesCount))
		time.sleep(0.050)
	gyroOffset[0] = int(gyroSum[0]/samplesCount)
	gyroOffset[1] = int(gyroSum[1]/samplesCount)
	gyroOffset[2] = int(gyroSum[2]/samplesCount)
	print("gyro offsets: x={0:>+5d}, y={1:>+5d}, z={2:>+5d} (samples={3:>3d})\n".format(gyroOffset[0], gyroOffset[1], gyroOffset[2], samplesCount))
		

try:
	bus = SMBus(I2C_CHANNEL)
except:
	try:
		bus = SMBus(LEGACY_I2C_CHANNEL)
	except:
		print("Cannot open I2C device")
		sys.exit(1)

# Gyro full scale.
#write_reg(GYRO_CONFIG, 0)
# Sample rate divisor.
#write_reg(SMPLRT_DIV, 100)

calibrateAcc()
calibrateGyro()

while 1:

	start = time.time()

	accData = read_reg(ACCEL_XOUT_H, 6)
	gyroData = read_reg(GYRO_XOUT_H, 6)

	accValue[0] = struct.unpack("<h", struct.pack("<BB", accData[1], accData[0]))[0] - accOffset[0]
	accValue[1] = struct.unpack("<h", struct.pack("<BB", accData[3], accData[2]))[0] - accOffset[1]
	accValue[2] = struct.unpack("<h", struct.pack("<BB", accData[5], accData[4]))[0] - accOffset[2]

	gyroValue[0] = struct.unpack("<h", struct.pack("<BB", gyroData[1], gyroData[0]))[0] - gyroOffset[0]
	gyroValue[1] = struct.unpack("<h", struct.pack("<BB", gyroData[3], gyroData[2]))[0] - gyroOffset[1]
	gyroValue[2] = struct.unpack("<h", struct.pack("<BB", gyroData[5], gyroData[4]))[0] - gyroOffset[2]

	print("ACC: x={0:>+5d} ({1:>+5.3f} g), y={2:>+5d} ({3:>+5.3f} g), z={4:>+5d} ({5:>+5.3f} g)".format(accValue[0], accValue[0]/32768.0*2.0, accValue[1], accValue[1]/32768.0*2.0, accValue[2], accValue[2]/32768.0*2.0))
	print("GYRO: x={0:>+5d} ({1:>+8.3f} dps), y={2:>+5d} ({3:>+8.3f} dps), z={4:>+5d} ({5:>+8.3f} dps)".format(gyroValue[0], gyroValue[0]/32768.0*250.0, gyroValue[1], gyroValue[1]/32768.0*250.0, gyroValue[2], gyroValue[2]/32768.0*250.0))
	print("\r\n")
	
	# Communication frequency @ 20 Hz.
	time_diff = time.time() - start
	if time_diff < 0.050:
		time.sleep(0.050 - time_diff);
