# Raspberry Pi plant waterer thingy
# This script is meant to run repeatedly and automatically, for example once per day using cron.
# It scans moisture sensors, and runs water pumps if no moisture is detected.

import sys
import os
import RPi.GPIO as GPIO
import time
from file_writer import *


# Load configuration
debugmode = False           # If true, prints out a lot of text when running the script. Specified in config.txt. Not needed if everything works.
discordbot = False          # If true, sends messages through discord. Specified in config.txt. If set to False, you don't need to set up a discord bot.
sensor_power_gpio = 0

try:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))       # This is a way to open a file in the same directory as the main program. (Python can be started from a different "home directory", causing an error if only a simple file name is used.)
    f = open(os.path.join(__location__, 'config.txt'), 'r')
    config_data = f.readlines()
except:
    print('Error reading configuration file (config.txt)')
    sys.exit(1)

# create plants (dictionaries) according to the config.txt file. A plant contains its name, its moisture sensor number, its water pump number, and the duration (seconds) of water pumping. The numbers (BCM) indicate which GPIO pin they are connected to.
plants = []
for configline in config_data:
    config = configline.split(';')
    if config[0] == 'Debug_mode' and config[1].rstrip() == 'true':
        debugmode = True
    if config[0] == 'Discord_bot_enabled' and config[1].rstrip() == 'true':
        discordbot = True
    if config[0] == 'Plant':
        plant_name = config[1]
        sensor_gpio = int(config[2])
        pump_gpio = int(config[3])
        pump_time = int(config[4].rstrip())
        plant = {'name':plant_name, 'sensor_gpio':sensor_gpio, 'pump_gpio':pump_gpio, 'pump_time':pump_time}
        if pump_time == 0: print(F"Warning: pump time for {plant_name} is set to 0 seconds")
        plants.append(plant)
    if config[0] == 'Sensor_power_gpio':
        sensor_power_gpio = int(config[1].rstrip())

# exit if the script resulted in error last time and it was not addressed
if os.path.isfile('ERROR.txt'):
    print('\nThis script caused an error last time, so it will not be run again until resolved. Look in ERROR.txt for information. If the issue is resolved, delete ERROR.txt to resume normal operation.')
    if discordbot: discord_notify("Irrigator aborted because an error is unresolved (see ERROR.txt).")
    sys.exit(1)

# exit if sensor power gpio was not set (not in configuration file or failed in some other way)
if sensor_power_gpio == 0:
    print("Error: GPIO pin for the sensor power relay not set. Exiting. See config.txt.")
    if discordbot: discord_notify("Irrigator aborted because sensor power gpio was not configured. See config.txt.")
    sys.exit(1)

# print configuration if debug mode is enabled
if debugmode == True:
    print('Plants:')
    for plant in plants:
        print(F"{plant['name']}: \tsensor {plant['sensor_gpio']}, \tpump {plant['pump_gpio']}")
    print(F'sensor power gpio: {sensor_power_gpio}')

# end of configuration, begin script

GPIO.setmode(GPIO.BCM)      # This line is always required when using RasPi GPIO pins. It specifies whether "BCM" or "BOARD" numbering is used.

# turn on the power relay for moisture sensors, and get readings
def scan_moisture():
    dry_plants = []
    if debugmode == True: print("Turning on power for sensors")
    GPIO.setup(sensor_power_gpio, GPIO.OUT)
    GPIO.output(sensor_power_gpio, GPIO.HIGH)
    time.sleep(1)           # give the relay and sensors a second to activate

    plants_are_moist = True
    for plant in plants:
        sensor = plant['sensor_gpio']
        GPIO.setup(sensor, GPIO.IN)
        input = GPIO.input(sensor)  # sensor returns 0 if moist, 1 if dry
        if debugmode == True: print(F"sensor for {plant['name']}: {input}")
        if input == 1: dry_plants.append(plant)   # if the sensor reported 1 (dry), add this plant to a list of plants that need watering

    # turn off the power relay for sensors
    if debugmode == True: print("Turning off power for sensors")
    GPIO.output(sensor_power_gpio, GPIO.LOW)

    return dry_plants

dry_plants = scan_moisture()
# We now have a list of plants that need watering.
# Firstly, if the list is empty, it means all plants are moist. No water pumping needed, just write the log and exit.
if not dry_plants:
    if debugmode == True: print("All plants are moist. _b No need for pumping water - exiting.")

    append_log("All plants moist, did not pump any water.")
    GPIO.cleanup()
    sys.exit(0)

# this function pumps water for the specified plant, for the duration specified for each plant in config.txt
def pump_water(plant):
    pump_time = plant['pump_time']
    if debugmode == True: print(F"Pumping water for {plant['name']} for {pump_time} seconds")
    pump = plant['pump_gpio']
    GPIO.setup(pump, GPIO.OUT)
    GPIO.output(pump, GPIO.HIGH)
    GPIO.output(pump, GPIO.LOW)
    time.sleep(pump_time)
    GPIO.output(pump, GPIO.HIGH)
    if debugmode == True: print(F"Stopping pump for {plant['name']}")
    time.sleep(1)

watered_plants = []
# go through the list of dry plants, and pump water for each of them
for plant in dry_plants:
    pump_water(plant)
    watered_plants.append(plant)

# Wait for a few seconds for water to settle, then check the moisture sensors again. If all report moist as they should, write the log and exit.
time.sleep(5)
if debugmode == True: print("Watering done, checking sensors again:")
dry_plants = scan_moisture()
if not dry_plants:
    logtext = "\n Watered plants: "
    for plant in watered_plants:
        logtext = logtext + plant['name'] + ", "
    logtext = logtext[:-2]
    append_log(logtext)
    GPIO.cleanup()
    sys.exit(0)


# If moisture sensors still report dry after watering, something is wrong with the physical installation (e.g. ran out of water, water missed the sensor, or pumps or sensors are not working)
if dry_plants:
    append_log("Plants still dry after attempted watering. Check the physical installation.")
    write_error("Plants still dry after attempted watering. Check the physical installation.")                  # this prevents the script from running again until resolved (writes ERROR.txt)
    if discordbot: discord_notify("Irrigator detected plants still dry after attempted watering. Check the physical installation.")
    GPIO.cleanup()
    sys.exit(1)


# This line should never be reached (both if statements above lead to an exit), but end program with a GPIO cleanup anyway just in case.
# Using GPIO can give errors/warnings if not "cleaned up" after use.
GPIO.cleanup()