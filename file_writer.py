# Relocated these file operations to simplify the main program a little.

import os
from datetime import datetime

def discord_notify(message):
    try:
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))           # This is a way to open a file in the same directory as the main program. (Python can be started from a different "home directory", causing an error if only a simple file name is used.)
        f = open(os.path.join(__location__, 'messages.txt'), 'a')
        f.write(message)
        f.close()
    except:
        print("Unable to write a message for the discord bot.")

def append_log(message):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d, %H:%M:%S")       # A string containing current date and time, e.g. "2021-08-12, 01:17:33".

    logtext = "\n-----\n"
    logtext = logtext + current_time + "\n"
    logtext = logtext + message
    logtext = logtext + "\n-----\n"
    print(logtext)

    try:
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        f = open(os.path.join(__location__, 'irrigation_log.txt'), 'a')
        f.write(logtext)
        f.close()
    except:
        print("Unable to write irrigation log.")

def write_error(message):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d, %H:%M:%S")       # A string containing current date and time, e.g. "2021-08-12, 01:17:33".
    errormessage = current_time + "\n" + message + "\nAfter addressing the error, remove this file to resume normal operation."
    try:
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        f = open(os.path.join(__location__, 'ERROR.txt'), 'w')
        f.write(errormessage)
        f.close()
    except:
        print("Unable to write to ERROR.txt")