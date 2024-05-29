# -*- coding:utf-8 -*-

import sys
import os
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from bmm150 import *

'''
  If you want to use SPI to drive this module, uncomment the codes below, and connect the module with Raspberry Pi via SPI port
  Connect to VCC，GND，SCK，SDO，SDI，CS，PS<-->GND pin
'''
RASPBERRY_PIN_CS =  27              #Chip selection pin when SPI is selected, use BCM coding method, the number is 27, corresponding to pin GPIO2
#bmm150 = bmm150_SPI(RASPBERRY_PIN_CS)

'''
  If you want to use I2C to drive this module, uncomment the codes below, and connect the module with Raspberry Pi via I2C port
  Connect to VCC，GND，SCL，SDA pin
'''
I2C_BUS         = 11   #default use I2C1
# I2C address select, that CS and SDO pin select 1 or 0 indicates the high or low level respectively. There are 4 combinations: 
ADDRESS_0       = 0x10   # (CSB:0 SDO:0)
ADDRESS_1       = 0x11   # (CSB:0 SDO:1)
ADDRESS_2       = 0x12   # (CSB:1 SDO:0)
ADDRESS_3       = 0x13   # (CSB:1 SDO:1) default i2c address
bmm150 = bmm150_I2C(I2C_BUS, ADDRESS_0)

geo_offsets_max = [-1000, -1000, -1000]
geo_offsets_min = [1000, 1000, 1000]
geo_offsets = [0, 0, 0]

def get_my_compass_degree():
    geomagnetic = bmm150.get_geomagnetic()
    compass = math.atan2(geomagnetic[0]-geo_offsets[0], geomagnetic[1]-geo_offsets[1])
    #correct the sensor orientation respect to the robot (90 degrees)
    compass = compass - (math.pi/2)
    if compass < 0:
      compass += 2 * math.pi
    if compass > 2 * math.pi:
     compass -= 2 * math.pi

    #if compass < 0:
    #  compass += 2 * math.pi
    
    return compass * 180 / math.pi  

def setup():
  while bmm150.ERROR == bmm150.sensor_init():
    print("sensor init error, please check connect") 
    time.sleep(1)
  bmm150.set_operation_mode(bmm150.POWERMODE_NORMAL)
  bmm150.set_preset_mode(bmm150.PRESETMODE_HIGHACCURACY)
  bmm150.set_rate(bmm150.RATE_10HZ)
  bmm150.set_measurement_xyz()
  
def loop():
  geomagnetic = bmm150.get_geomagnetic()
  print("mag x = %d ut    "%geomagnetic[0]) 
  print("mag y = %d ut    "%geomagnetic[1]) 
  print("mag z = %d ut    "%geomagnetic[2]) 
  degree = bmm150.get_compass_degree()
  print("the angle between the pointing direction and north is: %.2f "%degree) 
  print("my heading:  %.2f "%get_my_compass_degree())
  print("\r\b\r\b\r\b\r\b\r\b\r")
  time.sleep(0.1)

if __name__ == "__main__":
  try:
    setup()
    
    out = open("calibration.csv", "w")

    print("calibration start, make a full rotation with the robot")
    loop_count = 0
    while loop_count < 100:
      geomagnetic = bmm150.get_geomagnetic()
      out.write(str(geomagnetic[0]) + "," + str(geomagnetic[1]) + "," + str(geomagnetic[2]) + "\n")
      if(geo_offsets_max[0] < geomagnetic[0]):
        geo_offsets_max[0] = geomagnetic[0]
      if(geo_offsets_max[1] < geomagnetic[1]):
        geo_offsets_max[1] = geomagnetic[1]
      if(geo_offsets_max[2] < geomagnetic[2]):
        geo_offsets_max[2] = geomagnetic[2]
      if(geo_offsets_min[0] > geomagnetic[0]):
        geo_offsets_min[0] = geomagnetic[0]
      if(geo_offsets_min[1] > geomagnetic[1]):
        geo_offsets_min[1] = geomagnetic[1]
      if(geo_offsets_min[2] > geomagnetic[2]):
        geo_offsets_min[2] = geomagnetic[2]
      loop_count = loop_count + 1
      time.sleep(0.1)
      if(loop_count % 10 == 0):
        print(str(int((100-loop_count)/10)))
    print("calibration end")
    out.close()

    geo_offsets[0] = (geo_offsets_max[0] + geo_offsets_min[0])/2
    geo_offsets[1] = (geo_offsets_max[1] + geo_offsets_min[1])/2
    geo_offsets[2] = (geo_offsets_max[2] + geo_offsets_min[2])/2
    print("geo offsets: " + str(geo_offsets))

    while True:
        loop()
  except(KeyboardInterrupt):
    bmm150.set_operation_mode(bmm150.POWERMODE_SLEEP)
    print("\n\n\n\n\n")
