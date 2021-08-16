# Script to only test sensors and print their readings. 
# Keeps the power on for a minute (scanning every 10 seconds) so you can adjust the moisture detection threshold with the physical screw.
# Parts copied from the main program, hence some unnecessary code

import sys
import RPi.GPIO as GPIO
import time

# Load configuration
sensor_power_gpio = 0

try:
    with open('config.txt', 'r') as f:
        config_data = f.readlines()
except:
    print('Error reading configuration file (config.txt)')
    sys.exit()

plants = []
for configline in config_data:
    config = configline.split(';')
    # create plants (dictionaries) based on the configuration file. A plant contains its name, its moisture sensor number, and its water pump number. The numbers are GPIO (BCM) pin numbers.
    if config[0] == 'Plant':
        plant_name = config[1]
        sensor_gpio = int(config[2])
        pump_gpio = int(config[3].rstrip())
        plant = {'name':plant_name, 'sensor_gpio':sensor_gpio, 'pump_gpio':pump_gpio}
        plants.append(plant)
    if config[0] == 'Sensor_power_gpio':
        sensor_power_gpio = int(config[1].rstrip())

print('Plants:')
for plant in plants:
    print(F"{plant['name']}: \tsensor {plant['sensor_gpio']}, \tpump {plant['pump_gpio']}")
print(F'sensor power gpio: {sensor_power_gpio}')


# exit if sensor power gpio was not set (not in configuration file or failed in some other way)
if sensor_power_gpio == 0:
    print('Error: GPIO pin for the sensor power relay not set. Exiting.')
    sys.exit(1)

GPIO.setmode(GPIO.BCM)
print("Turning on power for sensors")
GPIO.setup(sensor_power_gpio, GPIO.OUT)
GPIO.output(sensor_power_gpio, GPIO.HIGH)
time.sleep(1)           # give the relay a second to activate

   
def scan_moisture():
    for plant in plants:
        sensor = plant['sensor_gpio']
        GPIO.setup(sensor, GPIO.IN)
        input = GPIO.input(sensor)
        print(F"sensor for {plant['name']}: {input}")
    
    time.sleep(10)

scan_moisture()
scan_moisture()
scan_moisture()
scan_moisture()
scan_moisture()
scan_moisture()

print("Turning off power for sensors")
GPIO.output(sensor_power_gpio, GPIO.LOW)

GPIO.cleanup()