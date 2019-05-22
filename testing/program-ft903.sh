#!/bin/sh

# Program the firmware
sudo dfu-util -d 0403:0fde -D /home/pi/Pi-puck/FT903/Pi-puck_FT903_Firmware_DFU.bin

# Reset FT903
echo Resetting FT903...
gpio write 27 0
sleep 0.1
gpio write 27 1

# Wait for 3 seconds and the USB camera device should be back
sleep 3
echo Done.

