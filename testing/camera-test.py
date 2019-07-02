#!/usr/bin/env python3

import time
import sys
import smbus
import subprocess

I2C_CHANNEL = 4
SENSOR_I2C_ADDR = 0x6e
OV7670_ADDR = 0x21

BANK_REGISTER = 0x3
BANK_A = 0x0
BANK_B = 0x1
BANK_C = 0x2
BANK_D = 0x3


######################
## PO8030 registers ##
######################
# Bank A registers
PO8030_REG_FRAMEWIDTH_H = 0x04
PO8030_REG_FRAMEWIDTH_L = 0x05
PO8030_REG_FRAMEHEIGHT_H = 0x06
PO8030_REG_FRAMEHEIGHT_L = 0x07
PO8030_REG_WINDOWX1_H = 0x08
PO8030_REG_WINDOWX1_L = 0x09
PO8030_REG_WINDOWY1_H = 0x0A
PO8030_REG_WINDOWY1_L = 0x0B
PO8030_REG_WINDOWX2_H = 0x0C
PO8030_REG_WINDOWX2_L = 0x0D
PO8030_REG_WINDOWY2_H = 0x0E
PO8030_REG_WINDOWY2_L = 0x0F
PO8030_REG_VSYNCSTARTROW_H = 0x10
PO8030_REG_VSYNCSTARTROW_L = 0x11
PO8030_REG_VSYNCSTOPROW_H = 0x12
PO8030_REG_VSYNCSTOPROW_L = 0x13
PO8030_REG_INTTIME_H = 0x17
PO8030_REG_INTTIME_M = 0x18
PO8030_REG_INTTIME_L = 0x19
PO8030_REG_WB_RGAIN = 0x23
PO8030_REG_WB_GGAIN = 0x24
PO8030_REG_WB_BGAIN = 0x25
PO8030_REG_AUTO_FWX1_H = 0x35
PO8030_REG_AUTO_FWX1_L = 0x36
PO8030_REG_AUTO_FWX2_H = 0x37
PO8030_REG_AUTO_FWX2_L = 0x38
PO8030_REG_AUTO_FWY1_H = 0x39
PO8030_REG_AUTO_FWY1_L = 0x3A
PO8030_REG_AUTO_FWY2_H = 0x3B
PO8030_REG_AUTO_FWY2_L = 0x3C
PO8030_REG_AUTO_CWX1_H = 0x3D
PO8030_REG_AUTO_CWX1_L = 0x3E
PO8030_REG_AUTO_CWX2_H = 0x3F
PO8030_REG_AUTO_CWX2_L = 0x40
PO8030_REG_AUTO_CWY1_H = 0x41
PO8030_REG_AUTO_CWY1_L = 0x42
PO8030_REG_AUTO_CWY2_H = 0x43
PO8030_REG_AUTO_CWY2_L = 0x44
PO8030_REG_PAD_CONTROL = 0x5B
PO8030_REG_SOFTRESET = 0x69
PO8030_REG_CLKDIV = 0x6A
PO8030_REG_BAYER_CONTROL_01 = 0x6C # Vertical/horizontal mirror.
# Bank B registers
PO8030_REG_ISP_FUNC_2 = 0x06 # Embossing, sketch, proximity.
PO8030_REG_FORMAT = 0x4E
PO8030_REG_SKETCH_OFFSET = 0x8F
PO8030_REG_SCALE_X = 0x93
PO8030_REG_SCALE_Y = 0x94
PO8030_REG_SCALE_TH_H = 0x95
PO8030_REG_SCALE_TH_L = 0x96
PO8030_REG_CONTRAST = 0x9D
PO8030_REG_BRIGHTNESS = 0x9E
PO8030_REG_SYNC_CONTROL0 = 0xB7
# Bank C registers
PO8030_REG_AUTO_CONTROL_1 = 0x04 # AutoWhiteBalance, AutoExposure.
PO8030_REG_EXPOSURE_T = 0x12
PO8030_REG_EXPOSURE_H = 0x13
PO8030_REG_EXPOSURE_M = 0x14
PO8030_REG_EXPOSURE_L = 0x15
PO8030_REG_SATURATION = 0x2C

# Formats
FORMAT_CBYCRY = 0x00
FORMAT_CRYCBY = 0x01
FORMAT_YCBYCR = 0x02
FORMAT_YCRYCB = 0x03
FORMAT_RGGB = 0x10
FORMAT_GBRG = 0x11
FORMAT_GRBG = 0x12
FORMAT_BGGR = 0x13
FORMAT_RGB565 = 0x30
FORMAT_RGB565_BYTE_SWAP = 0x31
FORMAT_BGR565 = 0x32
FORMAT_BGR565_BYTE_SWAP = 0x33
FORMAT_RGB444 = 0x36
FORMAT_RGB444_BYTE_SWAP = 0x37
FORMAT_DPC_BAYER = 0x41
FORMAT_YYYY = 0x44

######################
## OV7670 registers ##
######################
REG_CLKRC = 0x11 # Clocl control
REG_COM7 = 0x12 # Control 7
REG_COM10 = 0x15 # Control 10
COM7_FMT_VGA = 0x00
COM7_YUV = 0x00 # YUV
COM7_RGB = 0x04 # bits 0 and 2 - RGB format
REG_TSLB = 0x3a # lots of stuff
REG_COM11 = 0x3b # Control 11
REG_COM15 = 0x40 # Control 15
COM15_R00FF = 0xc0 # 00 to FF
COM15_RGB565 = 0x10 # RGB565 output
REG_HSTART = 0x17 # Horiz start high bits
REG_HSTOP = 0x18 # Horiz stop high bits
REG_VSTART = 0x19 # Vert start high bits
REG_VSTOP = 0x1a # Vert stop high bits
REG_VREF = 0x03 # Pieces of GAIN, VSTART, VSTOP
REG_HREF = 0x32 # HREF pieces
REG_RGB444 = 0x8c # RGB 444 control
REG_COM9 = 0x14 # Control 9  - gain ceiling
REG_COM13 = 0x3d # Control 13
COM13_GAMMA = 0x80 # Gamma enable
COM13_UVSAT = 0x40 # UV saturation auto adjustment

poXXXX_detected = False
ov7670_detected = False

def po3030_init():
	##############################################################################
	## Set output format to YCbYCr (see table on page 64 of PO3030K data sheet) ##
	##############################################################################

	bus.write_byte_data(SENSOR_I2C_ADDR, 0x4E, 0x02) # Format = Y Cb Y Cr
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x50, 0x40) # "Reserved"
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x9B, 0x00) # Brightness
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x9C, 0x96) # Y Contrast

	########################################################################
	## Set frame size to 960x512 to slow the maximum frame rate to 15 fps ##
	########################################################################

	frame_width = 960-1
	frame_height = 512-1

	bus.write_byte_data(SENSOR_I2C_ADDR, 0x04, (frame_width >> 8) & 0xFF) # Frame width, high
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x05, frame_width & 0xFF) # Frame width, low
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x06, (frame_height >> 8) & 0xFF) # Frame height, high
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x07, frame_height & 0xFF) # Frame height, low

	## Disable Auto Exposure - locks framerate to 15fps but might not always be desirable
	bus.write_byte_data(SENSOR_I2C_ADDR, 0xD4, 0x2C)

	## Disable HSYNC outside of active region (i.e. during VSYNC) (see p34 of datasheet)
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x4F, 0x2) # Image Signal Processor (ISP) Control 3 - set HD to 0



def po6030_init():
	##############################################################################################
	## Set image output size to VGA mode (640x480) (see table on page 60 of PO6030K data sheet) ##
	##############################################################################################

	x1 = 7
	y1 = 7
	x2 = 646
	y2 = 486

	bus.write_byte_data(SENSOR_I2C_ADDR, BANK_REGISTER, BANK_B) # Switch to Bank B
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x50, (x1 >> 8) & 0xFF) # Window_X1_H
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x51, x1 & 0xFF) # Window_X1_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x52, (y1 >> 8) & 0xFF) # Window_Y1_H
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x53, y1 & 0xFF) # Window_Y1_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x54, (x2 >> 8) & 0xFF) # Window_X2_H
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x55, x2 & 0xFF) # Window_X2_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x56, (y2 >> 8) & 0xFF) # Window_Y2_H
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x57, y2 & 0xFF) # Window_Y2_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x61, 0x0C) # VsyncStartRow_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x63, 0xEC) # VsyncStopRow_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x80, 0x20) # Scale_X
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x81, 0x20) # Scale_Y
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x82, 0x01) # Reserved
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x68, 0x00) # SyncControl0

	## Would it also be useful to disable Auto Exposure here for a constant frame rate?

	bus.write_byte_data(SENSOR_I2C_ADDR, BANK_REGISTER, BANK_C) # Switch to Bank C
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x11, 0x25) # AEWin_X_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x13, 0x1C) # AEWin_Y_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x14, 0x02) # AEWinWidth_H
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x15, 0x60) # AEWinWidth_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x16, 0x01) # AEWinHeight_H
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x17, 0xBE) # AEWinHeight_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x19, 0xE5) # AECenterWin_X_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x1B, 0x87) # AECenterWin_Y_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x1D, 0xA0) # AECenterWidth_L
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x1F, 0xA0) ## AECenterHeight_L

	##############################################################################
	## Set output format to YCbYCr (see table on page 67 of PO6030K data sheet) ##
	##############################################################################

	bus.write_byte_data(SENSOR_I2C_ADDR, BANK_REGISTER, BANK_B) # Switch to Bank B
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x38, 0x02) # Format = Y Cb Y Cr
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x90, 0xE0) # CS max = YCbCr range
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x91, 0x37) # Y contrast
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x92, 0x10) # Brightness
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x93, 0xEB) # Y max = YCbCr range

	#######################################################################################################################
	## Rotate the image by 180 degrees, by flipping both horizontally and vertically (see page 78 of PO6030K data sheet) ##
	#######################################################################################################################

	bus.write_byte_data(SENSOR_I2C_ADDR, BANK_REGISTER, BANK_B) # Switch to Bank B
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x68, 0x60) # SyncControl0 - enable Hsync and Vsync drop

	bus.write_byte_data(SENSOR_I2C_ADDR, BANK_REGISTER, BANK_A) # Switch to Bank A
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x90, 0xF5) # BayerControl01 - enable horizontal and vertical mirror

	time.sleep(0.035) # Must wait 1 (preview) frame time

	bus.write_byte_data(SENSOR_I2C_ADDR, BANK_REGISTER, BANK_B) # Switch to Bank B
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x68, 0x00) # SyncControl0 - disable Hsync and Vsync drop

	########################################################################
	## Set frame size to 960x512 to slow the maximum frame rate to 15 fps ##
	########################################################################

	frame_width = 960-1
	frame_height = 512-1

	bus.write_byte_data(SENSOR_I2C_ADDR, BANK_REGISTER, BANK_B) # Switch to Bank B
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x48, (frame_width >> 8) & 0xFF) # Frame width, high
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x49, frame_width & 0xFF) # Frame width, low
	# These registers are mentioned on page 7 of data sheet, but page 26 suggests they have something to do with flicker?
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x29, (frame_height >> 8) & 0xFF) # Frame height, high
	bus.write_byte_data(SENSOR_I2C_ADDR, 0x2A, frame_height & 0xFF) # Frame height, low



def po8030_init():
	bus.write_byte_data(SENSOR_I2C_ADDR, BANK_REGISTER, BANK_A)

	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_PAD_CONTROL, 0x00)

	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_WINDOWX1_H, 0x00)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_WINDOWX1_L, 0x01)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_WINDOWY1_H, 0x00)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_WINDOWY1_L, 0x01)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_WINDOWX2_H, 0x02)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_WINDOWX2_L, 0x80)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_WINDOWY2_H, 0x01)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_WINDOWY2_L, 0xE0)

	# AE full window selection.
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_FWX1_H, 0x00)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_FWX1_L, 0x01)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_FWX2_H, 0x02)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_FWX2_L, 0x80)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_FWY1_H, 0x00)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_FWY1_L, 0x01)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_FWY2_H, 0x01)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_FWY2_L, 0xE0)

	# AE center window selection.
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_CWX1_H, 0x00)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_CWX1_L, 0xD6)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_CWX2_H, 0x01)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_CWX2_L, 0xAB)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_CWY1_H, 0x00)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_CWY1_L, 0xA1)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_CWY2_H, 0x01)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_AUTO_CWY2_L, 0x40)

	bus.write_byte_data(SENSOR_I2C_ADDR, BANK_REGISTER, BANK_B)

	# Scale settings.
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_SCALE_X, 0x20)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_SCALE_Y, 0x20)

	# Format
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_FORMAT, FORMAT_YCBYCR)

	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_SYNC_CONTROL0, 0x00)

	bus.write_byte_data(SENSOR_I2C_ADDR, BANK_REGISTER, BANK_A)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_VSYNCSTARTROW_L, 0x0A)

	# Seems to cause image tearing?
	bus.write_byte_data(SENSOR_I2C_ADDR, BANK_REGISTER, BANK_B)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_SCALE_TH_H, 0x00)
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_SCALE_TH_L, 0x0A)

	###################################################################################
	## Set frame size to 960x512 or 875x800 to slow the maximum frame rate to 15 fps ##
	###################################################################################

	# 960x512 for 14.7456Mhz pixel clock on e-puck1
	# frame_width = 960-1
	# frame_height = 512-1

	# 875x800 for 21MHz pixel clock on e-puck2
	frame_width = 875-1
	frame_height = 800-1

	bus.write_byte_data(SENSOR_I2C_ADDR, BANK_REGISTER, BANK_A) # Switch to Bank A
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_FRAMEWIDTH_H, (frame_width >> 8) & 0xFF) # Frame width, high
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_FRAMEWIDTH_L, frame_width & 0xFF) # Frame width, low
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_FRAMEHEIGHT_H, (frame_height >> 8) & 0xFF) # Frame height, high
	bus.write_byte_data(SENSOR_I2C_ADDR, PO8030_REG_FRAMEHEIGHT_L, frame_height & 0xFF) # Frame height, low


def ov7670_init():
	bus.write_byte_data(OV7670_ADDR, REG_COM7, 0x80) #Reset to default values.
	time.sleep(0.2)
	bus.write_byte_data(OV7670_ADDR, REG_CLKRC, 0x80) #No internal clock prescaler.
	bus.write_byte_data(OV7670_ADDR, REG_TSLB, 0x04)
	bus.write_byte_data(OV7670_ADDR, REG_COM7, COM7_YUV|COM7_FMT_VGA) # Output format: YUV, VGA.
	bus.write_byte_data(OV7670_ADDR, REG_COM15, COM15_R00FF)
	bus.write_byte_data(OV7670_ADDR, REG_COM13, 0x00)
	bus.write_byte_data(OV7670_ADDR, 0xb0, 0x84) # Color mode?? (Not documented!)
	
	bus.write_byte_data(OV7670_ADDR, REG_HSTART, 0x13) # start = HSTART<<3 + HREF[2:0] = 19*8 + 6 = 158
	bus.write_byte_data(OV7670_ADDR, REG_HSTOP, 0x01) # stop = HSTOP<<3 + HREF[5:3] = 1*8 + 6 = 14 (158+640-784)
	bus.write_byte_data(OV7670_ADDR, REG_HREF, 0x36) # With flag "edge offset" set, then the image is strange (too much clear, not sharp); so clear this bit.
	bus.write_byte_data(OV7670_ADDR, REG_VSTART, 0x02) # start = VSTART<<2 + VREF[1:0] = 2*4 + 2 = 10
	bus.write_byte_data(OV7670_ADDR, REG_VSTOP, 0x7a) # stop = VSTOP<<2 + VREF[3:2] = 122*4 + 2 = 490
	bus.write_byte_data(OV7670_ADDR, REG_VREF, 0x0a)
	
	bus.write_byte_data(OV7670_ADDR, 0x0c, 0x00)
	bus.write_byte_data(OV7670_ADDR, 0x3e, 0x00)
	bus.write_byte_data(OV7670_ADDR, 0x70, 0x3a)
	bus.write_byte_data(OV7670_ADDR, 0x71, 0x35)
	bus.write_byte_data(OV7670_ADDR, 0x72, 0x11)
	bus.write_byte_data(OV7670_ADDR, 0x73, 0xf0)
	bus.write_byte_data(OV7670_ADDR, 0xa2, 0x02)
	
try:
	bus = smbus.SMBus(I2C_CHANNEL)
except:
	sys.exit(1)
	
try:
	p = subprocess.call("/home/pi/Pi-puck/camera-configuration")
	if (p == 0):
		ov7670_detected = True
except OSError as e:
	ov7670_detected = False
except:
	sys.exit(1)

if ov7670_detected == False:
	try:
		data = bus.read_i2c_block_data(SENSOR_I2C_ADDR, 0x00, 2)
		poXXXX_detected = True
	except OSError as e:
		poXXXX_detected = False
	except:
		sys.exit(1)

if poXXXX_detected:
	sensor_id = (data[0] << 8) + data[1]
	if sensor_id == 0x3030:
		try:
			po3030_init()
		except:
			sys.exit(1)
	elif sensor_id == 0x6030:
		try:
			po6030_init()
		except:
			sys.exit(1)
	elif sensor_id == 0x8030:
		try:
			po8030_init()
		except:
			sys.exit(1)		
	else:
		sys.exit(2)

#if ov7670_detected:
#	sensor_id = (data[0] << 8) + data[1]	
#	if sensor_id == 0x7673:
#		try:
#			ov7670_init()
#		except:
#			sys.exit(1)			
#	else:
#		sys.exit(2)

sys.exit(0)
		

