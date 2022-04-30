#!/usr/bin/python -u
# Author: Mrfixit2001 - Enables LED and Monitors for the buttons on the ROSHAMBO Super Famicom and Kintaro SNES Case

import time
import os
import subprocess
import string

import R64.GPIO as GPIO
# The R64.GPIO package is available here: https://github.com/mrfixit2001/Rock64-R64.GPIO
# NOTE: the R64GPIO package doesn't support "add_event_detect", so we can't use callbacks

# Initialize
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
PCB = 10
RESET = 3
POWER = 5
LED = 7
FAN = 8

# Tell the script if this is running on a ROCK64 or ROCKPRO64
GPIO.setrock("ROCK64")

# Setup 
GPIO.setup(PCB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RESET, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(POWER, GPIO.IN)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(FAN, GPIO.OUT)
IGNORE_PWR_OFF = False
if(GPIO.input(POWER) == "0"):
	# System was started with power switch off
	IGNORE_PWR_OFF = True

# Turn on LED AND FAN
GPIO.output(LED, GPIO.HIGH)
GPIO.output(FAN, GPIO.HIGH)

# Function that blinks LED once when button press is detected
def Blink_LED():
	GPIO.output(LED, GPIO.LOW)
	time.sleep(0.2)
	GPIO.output(LED, GPIO.HIGH)
			
# Monitor for Inputs
while True:
	if(GPIO.input(PCB) == "0"):
		if(GPIO.input(RESET) == "0"):
			print("Rebooting...")
			Blink_LED()
			os.system("reboot")
			break
		if(GPIO.input(POWER) == "1" and IGNORE_PWR_OFF == True):
			IGNORE_PWR_OFF = False
		if(GPIO.input(POWER) == "0" and IGNORE_PWR_OFF == False):
			rockCheck = subprocess.check_output("cat /sys/firmware/devicetree/base/rockchip-suspend/status", shell=True).decode().strip().lower()
			if(''.join(filter(lambda c: c in string.printable, rockCheck)) == "okay"):
				print("Suspending...")
				GPIO.output(LED, GPIO.LOW)
				GPIO.output(FAN, GPIO.LOW)
				os.system("ifconfig eth0 down")
				os.system("echo mem > /sys/power/state")
				time.sleep(1)
				os.system("ifconfig eth0 up")
				GPIO.output(LED, GPIO.HIGH)
				GPIO.output(FAN, GPIO.HIGH)
			else:
				print("Shutting down...")
				Blink_LED()
				GPIO.output(FAN, GPIO.LOW)
				os.system("shutdown -h now")
				break
	else:
		break
	time.sleep(0.3)

GPIO.output(FAN, GPIO.LOW)
GPIO.cleanup()
