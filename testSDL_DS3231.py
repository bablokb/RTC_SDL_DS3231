#!/usr/bin/env python
"""
 Test SDL_DS3231
 John C. Shovic, SwitchDoc Labs
 08/03/2014

Additional code added by Conrad Storz in 2015 and 2016
"""

# imports

#import sys
import time
import datetime
import random
import SDL_DS3231

# Main Program

print
print "Test SDL_DS3231 Version 1.0 - SwitchDoc Labs"
print
print
print "Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S")
print

#FILENAME = time.strftime("%Y-%m-%d%H:%M:%SRTCTest") + ".txt"
STARTTIME = datetime.datetime.utcnow()

DS3231 = SDL_DS3231.sdl_ds3231(1, 0x68)
#comment out the next line after the clock has been initialized
DS3231.write_system_datetime_now()

# Main Loop - sleeps 10 seconds, then reads and prints values of all clocks
# Also reads two bytes of EEPROM and writes the next value to the two bytes

# do the AT24C32 eeprom

print "----------------- "
print "----------------- "
print " Test the AT24C32 EEPROM"
print "----------------- "
print "writing first 10 addresses with random data"
for x in range(0, 10):
    value = random.randint(0, 255)
    print "address = %i writing value = %i" % (x, value)
    DS3231.write_at24c32_byte(x, value)
print "----------------- "

print "reading first 10 addresses"
for x in range(0, 10):
    print "address = %i value = %i" %(x, DS3231.read_at24c32_byte(x))
print "----------------- "
print "----------------- "


while True:
    CURRENTTIME = datetime.datetime.utcnow()
    #DELTATIME = CURRENTTIME - STARTTIME
    print
    print "Raspberry Pi = \t" + time.strftime("%Y-%m-%d %H:%M:%S")
    print "DS3231 = \t\t%s" % DS3231.read_datetime()
    print "DS3231 Temperature = ", DS3231.get_temp()
    time.sleep(10.0)
