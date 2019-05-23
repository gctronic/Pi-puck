#!/bin/sh

sudo rmmod ads1015 > /dev/null 2>&1
python3 read-battery.py