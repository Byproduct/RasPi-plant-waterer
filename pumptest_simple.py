# Script to test pumps. Replace number 21 with the correct GPIO BCM number.

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(21,GPIO.OUT)
GPIO.output(21,GPIO.LOW)
time.sleep(5)
GPIO.output(21,GPIO.HIGH)
GPIO.cleanup()