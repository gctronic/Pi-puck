from smbus2 import SMBus, i2c_msg
import sys
import time

I2C_CHANNEL = 12
LEGACY_I2C_CHANNEL = 4
ROB_ADDR = 0x1F
ACTUATORS_SIZE = (19+1) # Data + checksum.
SENSORS_SIZE = (46+1) # Data + checksum.

actuators_data = bytearray([0] * ACTUATORS_SIZE)
sensors_data = bytearray([0] * SENSORS_SIZE)
prox = [0 for x in range(8)]
prox_amb = [0 for x in range(8)]
mic = [0 for x in range(4)]
mot_steps = [0 for x in range(2)]

def update_robot_sensors_and_actuators():
	global sensors_data
	global actuators_data
	try:
		write = i2c_msg.write(ROB_ADDR, actuators_data)
		read = i2c_msg.read(ROB_ADDR, SENSORS_SIZE)
		bus.i2c_rdwr(write, read)
		sensors_data = list(read)
	except:
		sys.exit(1)

try:
	bus = SMBus(I2C_CHANNEL)
except:
	try:
		bus = SMBus(LEGACY_I2C_CHANNEL)
	except:
		print("Cannot open I2C device")
		sys.exit(1)


counter = 0
actuators_state = 0

while 1:

	start = time.time()
	
	counter += 1
	if(counter == 20):
		counter = 0
		if(actuators_state == 0):
			actuators_data[0] = 0		# Left speed: 512
			actuators_data[1] = 2
			actuators_data[2] = 0		# Right speed: -512
			actuators_data[3] = 0xFE
			actuators_data[4] = 0 		# Speaker sound
			actuators_data[5] = 0x0F	# LED1, LED3, LED5, LED7 on/off flag
			actuators_data[6] = 100		# LED2 red
			actuators_data[7] = 0		# LED2 green
			actuators_data[8] = 0		# LED2 blue
			actuators_data[9] = 100		# LED4 red
			actuators_data[10] = 0		# LED4 green
			actuators_data[11] = 0		# LED4 blue
			actuators_data[12] = 100	# LED6 red
			actuators_data[13] = 0		# LED6 green
			actuators_data[14] = 0		# LED6 blue
			actuators_data[15] = 100	# LED8 red
			actuators_data[16] = 0		# LED8 green
			actuators_data[17] = 0		# LED8 blue
			actuators_data[18] = 0 		# Settings.
			actuators_state = 1
		elif(actuators_state == 1):
			actuators_data[0] = 0		# Left speed: 0
			actuators_data[1] = 0
			actuators_data[2] = 0		# Right speed: 0
			actuators_data[3] = 0
			actuators_data[4] = 0 		# Speaker sound
			actuators_data[5] = 0x0		# LED1, LED3, LED5, LED7 on/off flag
			actuators_data[6] = 0		# LED2 red
			actuators_data[7] = 100		# LED2 green
			actuators_data[8] = 0		# LED2 blue
			actuators_data[9] = 0		# LED4 red
			actuators_data[10] = 100	# LED4 green
			actuators_data[11] = 0		# LED4 blue
			actuators_data[12] = 0		# LED6 red
			actuators_data[13] = 100	# LED6 green
			actuators_data[14] = 0		# LED6 blue
			actuators_data[15] = 0		# LED8 red
			actuators_data[16] = 100	# LED8 green
			actuators_data[17] = 0		# LED8 blue
			actuators_data[18] = 0		# Settings.
			actuators_state = 2
		elif(actuators_state == 2):
			actuators_data[0] = 0		# Left speed: 512
			actuators_data[1] = 2
			actuators_data[2] = 0		# Right speed: -512
			actuators_data[3] = 0xFE
			actuators_data[4] = 0 		# Speaker sound
			actuators_data[5] = 0x0F	# LED1, LED3, LED5, LED7 on/off flag
			actuators_data[6] = 0		# LED2 red
			actuators_data[7] = 0		# LED2 green
			actuators_data[8] = 100		# LED2 blue
			actuators_data[9] = 0		# LED4 red
			actuators_data[10] = 0		# LED4 green
			actuators_data[11] = 100	# LED4 blue
			actuators_data[12] = 0		# LED6 red
			actuators_data[13] = 0		# LED6 green
			actuators_data[14] = 100	# LED6 blue
			actuators_data[15] = 0		# LED8 red
			actuators_data[16] = 0		# LED8 green
			actuators_data[17] = 100	# LED8 blue
			actuators_data[18] = 0 		# Settings.
			actuators_state = 3
		elif(actuators_state == 3):
			actuators_data[0] = 0		# Left speed: 0
			actuators_data[1] = 0
			actuators_data[2] = 0		# Right speed: 0
			actuators_data[3] = 0
			actuators_data[4] = 0 		# Speaker sound
			actuators_data[5] = 0x0		# LED1, LED3, LED5, LED7 on/off flag
			actuators_data[6] = 100		# LED2 red
			actuators_data[7] = 100		# LED2 green
			actuators_data[8] = 0		# LED2 blue
			actuators_data[9] = 100		# LED4 red
			actuators_data[10] = 100	# LED4 green
			actuators_data[11] = 0		# LED4 blue
			actuators_data[12] = 100	# LED6 red
			actuators_data[13] = 100	# LED6 green
			actuators_data[14] = 0		# LED6 blue
			actuators_data[15] = 100	# LED8 red
			actuators_data[16] = 100	# LED8 green
			actuators_data[17] = 0		# LED8 blue
			actuators_data[18] = 0 		# Settings.
			actuators_state = 0

	checksum = 0
	for i in range(ACTUATORS_SIZE-1):
		checksum ^= actuators_data[i]		
	actuators_data[ACTUATORS_SIZE-1] = checksum

	update_robot_sensors_and_actuators()
	
	#if len(sensors_data) < 0:
	#	sys.exit(1)
	
	# Verify the checksum (Longitudinal Redundancy Check) before interpreting the received sensors data.
	checksum = 0
	for i in range(SENSORS_SIZE-1):
		checksum ^= sensors_data[i]
	if(checksum == sensors_data[SENSORS_SIZE-1]):
		for i in range(8):
			prox[i] = sensors_data[i*2+1]*256+sensors_data[i*2]
		print("prox: {0:4d}, {1:4d}, {2:4d}, {3:4d}, {4:4d}, {5:4d}, {6:4d}, {7:4d}\r\n".format(prox[0], prox[1], prox[2], prox[3], prox[4], prox[5], prox[6], prox[7]))
		
		for i in range(8):
			prox_amb[i] = sensors_data[16+i*2+1]*256+sensors_data[16+i*2]
		print("ambient: {0:4d}, {1:4d}, {2:4d}, {3:4d}, {4:4d}, {5:4d}, {6:4d}, {7:4d}\r\n".format(prox_amb[0], prox_amb[1], prox_amb[2], prox_amb[3], prox_amb[4], prox_amb[5], prox_amb[6], prox_amb[7]))
		
		for i in range(4):
			mic[i] = sensors_data[32+i*2+1]*256+sensors_data[32+i*2]
		print("mic: {0:4d}, {1:4d}, {2:4d}, {3:4d}\r\n".format(mic[0], mic[1], mic[2], mic[3]))
		
		print("sel: {0:2d}\r\n".format(sensors_data[40]&0x0F))
		print("button: {0:1d}\r\n".format(sensors_data[40]>>4))
		for i in range(2):
			mot_steps[i] = sensors_data[41+i*2+1]*256+sensors_data[41+i*2]
		print("steps: {0:4d}, {1:4d}\r\n".format(mot_steps[0], mot_steps[1]))
		print("tv: {0:2d}\r\n".format(sensors_data[45]))

		print("\r\n")
	else:
		print("wrong checksum ({0:#x} != {0:#x})\r\n".format(sensors_data[ACTUATORS_SIZE-1], checksum))
	
	# Communication frequency @ 20 Hz.
	time_diff = time.time() - start
	if time_diff < 0.050:
		time.sleep(0.050 - time_diff);
