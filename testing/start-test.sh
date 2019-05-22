#!/bin/sh

i2c_switch_error=0
robot_error=0
camera_error=0
i2c_rgb_error=0
adc_error=0

#################
# Test sequence #
#################
# Remove old files if any.
rm *.jpg > /dev/null 2>&1
rm *.wav > /dev/null 2>&1

# I2C switch testing
#python3 i2c_enable.py
#ret=$?
#if [ $ret -ne 0 ]; then
#	i2c_switch_error=1
#fi
# Print report
#if [ $i2c_switch_error -eq 0 ]; then
#	echo "I2C switch: OK\r\n";
#else
#	echo "I2C switch: FAILED\r\n";
#fi

# Robot communication testing
#if ! pgrep pigpiod > /dev/null; then
#	sudo pigpiod
#fi
if [ $i2c_switch_error -eq 0 ]; then
	python3 rob-comm-test.py
	ret=$?
	if [ $ret -eq 1 ]; then
		robot_error=1 # I2C error
	elif [ $ret -eq 2 ]; then
		robot_error=3 # Comm error (wrong value received)
	fi
else
	robot_error=2
fi
# Print report
if [ $robot_error -eq 0 ]; then
	echo "Robot: OK\r\n";
elif [ $robot_error -eq 2 ]; then
	echo "Robot: NOT TESTED\r\n";
elif [ $robot_error -eq 3 ]; then
	echo "Robot: FAILED (I2C robot: OK)\r\n";	
else
	echo "I2C robot: FAILED\r\n";
fi

# Camera configuration testing
if [ $i2c_switch_error -eq 0 ]; then
	python3 camera-test.py
	ret=$?
	if [ $ret -eq 1 ]; then
		camera_error=1 # I2C error
	elif [ $ret -eq 2 ]; then
		camera_error=3 # Comm error (configuration not completed correctly)
	fi
else
	camera_error=2
fi
# Print report
if [ $camera_error -eq 0 ]; then
	echo "Camera conf: OK\r\n";
elif [ $camera_error -eq 2 ]; then
	echo "Camera conf: NOT TESTED\r\n";
elif [ $camera_error -eq 3 ]; then
	echo "Camera conf: FAILED (I2C camera: OK)\r\n";	
else
	echo "I2C camera: FAILED\r\n";
fi

# Camera image grabbing testing
if [ $camera_error -eq 0 ]; then
	/home/pi/Pi-puck/snapshot/snapshot 1 0
	ret=$?
	if [ $ret -eq 1 ]; then
		camera_error=5 # Cannot grab an image
	fi	
else
	camera_error=4
fi
# Print report
if [ $camera_error -eq 0 ]; then
	echo "Camera grab: OK\r\n";
elif [ $camera_error -eq 4 ]; then
	echo "Camera grab: NOT TESTED\r\n";
elif [ $camera_error -eq 5 ]; then
	echo "Camera grab: FAILED (camera conf: OK)\r\n";
fi

# Speaker testing
echo "Testing speaker\r\n"
play -q -n -c 1 synth 2 sine 5000 &

# Microphone testing
arecord -Dmic_mono -c1 -r16000 -fS32_LE -twav -d2 test.wav > /dev/null 2>&1
#sleep 2
echo "Testing microphone\r\n"
aplay test.wav > /dev/null 2>&1

# RGB testing
if [ $i2c_switch_error -eq 0 ]; then
	python3 leds-test.py
	ret=$?
	if [ $ret -ne 0 ]; then
		i2c_rgb_error=1
	fi
else
	i2c_rgb_error=2
fi
# Print report
if [ $i2c_rgb_error -eq 0 ]; then
	echo "I2C RGB: OK\r\n";
elif [ $i2c_rgb_error -eq 2 ]; then
	echo "I2C RGB: NOT TESTED\r\n";
else
	echo "I2C RGB: FAILED\r\n";
fi

# Battery testing
sudo rmmod ads1015 > /dev/null 2>&1
if [ $i2c_switch_error -eq 0 ]; then
	python3 battery-test.py
	ret=$?
	if [ $ret -eq 1 ]; then
		adc_error=1 # I2C error
	elif [ $ret -eq 2 ]; then
		adc_error=3 # ADC error (too low)
	fi
else
	adc_error=2
fi
# Print report
if [ $adc_error -eq 0 ]; then
	echo "ADC: OK\r\n";
elif [ $adc_error -eq 2 ]; then
	echo "ADC: NOT TESTED\r\n";
elif [ $adc_error -eq 3 ]; then
	echo "ADC: FAILED (I2C ADC: OK)\r\n";	
else
	echo "I2C ADC: FAILED\r\n";
fi

# Sending image to pc
if [ $camera_error -eq 0 ]; then
	sx image01.jpg
fi


