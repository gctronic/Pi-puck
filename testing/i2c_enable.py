#!/usr/bin/env python3

import time
import sys
import smbus


I2C_CHANNEL = 3
I2C_ADDR = 0x70

try:
	bus = smbus.SMBus(I2C_CHANNEL)
	bus.write_byte_data(I2C_ADDR, 0x01, 0x03)
except:
	sys.exit(1)

sys.exit(0)

