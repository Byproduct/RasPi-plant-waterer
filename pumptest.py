# Script to only test pumps, based on the main program configuration. 
# Runs each pump for 5 seconds.

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

# initialize and set each pump to off (GPIO.HIGH)
print("\n\n")

GPIO.setmode(GPIO.BCM)
for plant in plants:
    gpionumber = int(plant['pump_gpio'])
    GPIO.setup(gpionumber,GPIO.OUT)
    GPIO.output(gpionumber,GPIO.HIGH)

for plant in plants:
    gpionumber = int(plant['pump_gpio'])
    print(F"Now pumping water for {plant['name']}")
    GPIO.output(gpionumber,GPIO.LOW)
    time.sleep(5)
    GPIO.output(gpionumber,GPIO.HIGH)
    time.sleep(2)

GPIO.cleanup()



