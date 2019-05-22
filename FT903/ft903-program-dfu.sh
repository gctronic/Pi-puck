#!/bin/sh

# Reset FT903
echo Resetting FT903...
gpio write 27 0
sleep 0.1
gpio write 27 1

# Wait for the device to reset, then send DFU enable command over I2C
sleep 1
echo Sending DFU enable I2C command...
i2cset -y 3 0x1c 0xff

# Wait for the USB interface to enumerate, then program the firmware
sleep 2
echo Attempting to program DFU firmware...
sudo dfu-util -d 0403:0fde -D "$1"

# Finally, reset FT903
echo Resetting FT903...
gpio write 27 0
sleep 0.1
gpio write 27 1

# Wait for 3 seconds and the USB camera device should be back
sleep 3
echo Done.
