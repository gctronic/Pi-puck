import pigpio
import time
import struct
import signal
import sys
from smbus2 import SMBus, i2c_msg
import subprocess

I2C_CHANNEL = 4
ROB_ADDR = 0x1F
ACTUATORS_SIZE = (19+1) # Data + checksum.
SENSORS_SIZE = (46+1) # Data + checksum.

I2C_CHANNEL_FT903 = 3
FT903_I2C_ADDR = 0x1C

CHARGE_PIN = 13

WALL_THR = 2000
WALL_THR1 = 500
BASE_SPEED = 150
MAX_SPEED = 250
MIN_SPEED = -250

speed_left = 0
speed_right = 0
actuators_data = bytearray([0] * ACTUATORS_SIZE)
sensors_data = bytearray([0] * SENSORS_SIZE)
charge_state = 0
charging_count = 0
loop_count = 0
leds_state = 0

def update_robot_sensors_and_actuators():
	global sensors_data
	global actuators_data
	try:
		write = i2c_msg.write(ROB_ADDR, actuators_data)
		read = i2c_msg.read(ROB_ADDR, SENSORS_SIZE)
		bus.i2c_rdwr(write, read)
		sensors_data = list(read)
	except:
		print("Comm error: " + str(sys.exc_info()[0]))
		#time.sleep(1)
		#sys.exit(1)

pi = pigpio.pi()
if not pi.connected:
   sys.exit(1)	

pi.set_mode(CHARGE_PIN, pigpio.INPUT)
pi.set_pull_up_down(CHARGE_PIN, pigpio.PUD_OFF)

try:
	bus = SMBus(I2C_CHANNEL)
except:
	print("Cannot open robot i2c bus: " + str(sys.exc_info()[0]))
	sys.exit(1)

try:
	bus_ft903 = SMBus(I2C_CHANNEL_FT903)
except:
	print("Cannot open ft903 i2c bus: " + str(sys.exc_info()[0]))
	sys.exit(1)	

	
#def signal_handler(sig, frame):
#		actuators_data[0] = 0
#		actuators_data[1] = 0
#		actuators_data[2] = 0
#		actuators_data[3] = 0
#		pi.i2c_write_device(handle, actuators_data)
#		(count, sensors_data) = pi.i2c_read_device(handle, SENSORS_SIZE)
#		sys.exit(0)
		
#signal.signal(signal.SIGINT, signal_handler)	

while True:

	start = time.time()

	try:
		#print("speed_left type = " + str(type(speed_left)))
		#print("speed_right type = " + str(type(speed_right)))

		#print(struct.pack('H', speed_right))
		#print(struct.unpack('BB', struct.pack('H', speed_right)))
		actuators_data[0] = struct.unpack('BB', struct.pack('H', speed_left))[0]
		actuators_data[1] = struct.unpack('BB', struct.pack('H', speed_left))[1]
		actuators_data[2] = struct.unpack('BB', struct.pack('H', speed_right))[0]
		actuators_data[3] = struct.unpack('BB', struct.pack('H', speed_right))[1]
		
		checksum = 0
		for i in range(ACTUATORS_SIZE-1):
			checksum ^= actuators_data[i]		
		actuators_data[ACTUATORS_SIZE-1] = checksum			
			
		update_robot_sensors_and_actuators()

		# Verify the checksum (Longitudinal Redundancy Check) before interpreting the received sensors data.
		checksum = 0
		for i in range(SENSORS_SIZE-1):
			checksum ^= sensors_data[i]
		if(checksum == sensors_data[SENSORS_SIZE-1]):		
		
			prox0 = sensors_data[1]*256+sensors_data[0]
			prox7 = sensors_data[15]*256+sensors_data[14]
						
			if charge_state == 1:
				speed_left = 0
				speed_right = 0
				if charging_count < 10:
					charging_count += 1
				if charging_count == 10: # Play sound after about half a second (based on comm. frequency loop)
					charging_count += 1
					subprocess.Popen("/usr/bin/aplay  /home/pi/Pi-puck/battery/charging_man.wav".split())					
				loop_count += 1
				if loop_count == 20:
					loop_count = 0
					if leds_state == 0:
						bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x00, 0x05) # Set LED1 to magenta
						bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x01, 0x02) # Set LED2 to green
						bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x02, 0x04) # Set LED3 to blue
					elif leds_state == 1:
						bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x00, 0x04) # Set LED1 to blue
						bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x01, 0x05) # Set LED2 to magenta
						bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x02, 0x02) # Set LED3 to green
					elif leds_state == 2:
						bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x00, 0x02) # Set LED1 to green
						bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x01, 0x04) # Set LED2 to blue
						bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x02, 0x05) # Set LED3 to magenta
					if leds_state == 2:
						leds_state = 0
					else:
						leds_state += 1						
			else:
				bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x00, 0x00) # Set LED1 off
				bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x01, 0x00) # Set LED2 off
				bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x02, 0x00) # Set LED3 off			
				loop_count = 0
				leds_state = 0
				charging_count = 0
				if (prox0>WALL_THR) or (prox7>WALL_THR):
					diff = int((prox0 - prox7)/10)
					speed_left = BASE_SPEED + diff
					speed_right = BASE_SPEED - diff
					
					if speed_left > MAX_SPEED:
						speed_left = MAX_SPEED
					elif speed_left < MIN_SPEED:
						speed_left = MIN_SPEED
						
					if speed_right > MAX_SPEED:
						speed_right = MAX_SPEED
					elif speed_right < MIN_SPEED:
						speed_right = MIN_SPEED	
				elif (prox0>WALL_THR1) or (prox7>WALL_THR1):
					speed_left = 300
					speed_right = 300
				else:
					speed_left = 500
					speed_right = 500
			
			if speed_left < 0:
				speed_left += 65536
			if speed_right < 0:
				speed_right += 65536	
			
			#print("prox0 = " + str(prox0) + ", prox7 = " + str(prox7) + "\r\n");
			
			charge_state = pi.read(CHARGE_PIN)
			#print("charge_state = " + str(charge_state) + "\r\n")
			
			#print("L=" + str(speed_left) + ", R=" + str(speed_right))
			
			#time.sleep(0.1)
		else:
			print("wrong checksum ({0:#x} != {0:#x})\r\n".format(sensors_data[ACTUATORS_SIZE-1], checksum))		
		
	except KeyboardInterrupt:
		print ("CTRL+C detected")
		break
	except:
		print("Error: " + str(sys.exc_info()[0]))
		time.sleep(1)
		#break

	# Communication frequency @ 20 Hz.
	time_diff = time.time() - start
	if time_diff < 0.050:
		time.sleep(0.050 - time_diff);
		
		
actuators_data[0] = 0
actuators_data[1] = 0
actuators_data[2] = 0
actuators_data[3] = 0
checksum = 0
for i in range(ACTUATORS_SIZE-1):
	checksum ^= actuators_data[i]		
actuators_data[ACTUATORS_SIZE-1] = checksum	
update_robot_sensors_and_actuators()

bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x00, 0x00) # Set LED1 off
bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x01, 0x00) # Set LED2 off
bus_ft903.write_byte_data(FT903_I2C_ADDR, 0x02, 0x00) # Set LED3 off

bus.close() # close the i2c bus
bus_ft903.close()