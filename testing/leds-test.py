#!/usr/bin/env python3

import time
import sys
import smbus


I2C_CHANNEL = 3
FT903_I2C_ADDR = 0x1C
loop = 0

try:
	bus = smbus.SMBus(I2C_CHANNEL)
	for loop in range (0,3):
		bus.write_byte_data(FT903_I2C_ADDR, 0x00, 0x01) # Set LED1 to red
		bus.write_byte_data(FT903_I2C_ADDR, 0x01, 0x01) # Set LED2 to red
		bus.write_byte_data(FT903_I2C_ADDR, 0x02, 0x01) # Set LED3 to red
		time.sleep(0.5)
		bus.write_byte_data(FT903_I2C_ADDR, 0x00, 0x02) # Set LED1 to green
		bus.write_byte_data(FT903_I2C_ADDR, 0x01, 0x02) # Set LED2 to green
		bus.write_byte_data(FT903_I2C_ADDR, 0x02, 0x02) # Set LED3 to green
		time.sleep(0.5)
		bus.write_byte_data(FT903_I2C_ADDR, 0x00, 0x04) # Set LED1 to blue
		bus.write_byte_data(FT903_I2C_ADDR, 0x01, 0x04) # Set LED2 to blue
		bus.write_byte_data(FT903_I2C_ADDR, 0x02, 0x04) # Set LED3 to blue
		time.sleep(0.5)	

	bus.write_byte_data(FT903_I2C_ADDR, 0x00, 0x00) # LED1 off
	bus.write_byte_data(FT903_I2C_ADDR, 0x01, 0x00) # LED2 off
	bus.write_byte_data(FT903_I2C_ADDR, 0x02, 0x00) # LED3 off
	
except:
	sys.exit(1)

sys.exit(0)

