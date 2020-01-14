import sys
import cv2
import argparse
import time

parser = argparse.ArgumentParser(description='Snapshot example')
parser.add_argument('-d', dest="d", type=int, default=0) # integer
parser.add_argument('-n', dest="n", type=int, default=1) # integer
parser.add_argument('-v', dest="v", action="store_true", default=False) # boolean

results = parser.parse_args()

print("d = " + str(results.d))
print("n = " + str(results.n))
print("v = " + str(results.v))

cam = cv2.VideoCapture(results.d)

if results.v:
	print("frame width = " + str(cam.get(cv2.CAP_PROP_FRAME_WIDTH)))
	print("frame height = " + str(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))
	print("fps = " + str(cam.get(cv2.CAP_PROP_FPS)))
	print("format = " + str(cam.get(cv2.CAP_PROP_FORMAT)))
	val = int(cam.get(cv2.CAP_PROP_FOURCC)) # Get Codec Type- Int form
	print("Input codec type: " + chr(val & 0XFF) + chr((val & 0XFF00) >> 8) + chr((val & 0XFF0000) >> 16) + chr((val & 0XFF000000) >> 24))
	
num_grab = results.n
if num_grab > 99:
	num_grab = 99

while num_grab > 0:
	start = time.time()
	ret, frame = cam.read()
	cv2.imwrite("image{0:02d}.jpg".format(results.n-num_grab), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
	num_grab -= 1
	if results.v:
		print("frame grabbed")
		
	# Grabbing frequency @ 5 Hz.
	time_diff = time.time() - start
	if time_diff < 0.2:
		time.sleep(0.2 - time_diff);