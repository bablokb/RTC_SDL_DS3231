#!/usr/bin/env python
"""
# SDL_DS3231.py Python Driver Code
# SwitchDoc Labs 12/19/2014
# V 1.2
# only works in 24 hour mode
# now includes reading and writing the AT24C32 included on the SwitchDoc Labs
#   DS3231 / AT24C32 Module (www.switchdoc.com

#encoding: utf-8

# Copyright (C) 2013 @XiErCh
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""

import time
import smbus
from datetime import datetime

# set I2c bus addresses of clock module and non-volatile ram 
DS3231ADDR = 0x68 #known versions of DS3231 use 0x68
AT24C32ADDR = 0x57  #older boards use 0x56

I2C_PORT = 1 #valid ports are 0 and 1

def _bcd_to_int(bcd):
    """
    Decode a 2x4bit BCD to a integer.
    """
    out = 0
    for digit in (bcd >> 4, bcd):
        for value in (1, 2, 4, 8):
            if digit & 1:
                out += value
            digit >>= 1
        out *= 10
    return out / 10


def _int_to_bcd(number):
    """
    Encode a one or two digits number to the BCD format.
    """
    bcd = 0
    for idx in (number // 10, number % 10):
        for value in (8, 4, 2, 1):
            if idx >= value:
                bcd += 1
                idx -= value
            bcd <<= 1
    return bcd >> 1


class sdl_ds3231():
    """
    Define the methods needed to read and update the real-time-clock module.
    """

    _SECONDS_REGISTER = 0x00
    _MINUTES_REGISTER = 0x01
    _HOURS_REGISTER = 0x02
    _DAY_OF_WEEK_REGISTER = 0x03
    _DAY_OF_MONTH_REGISTER = 0x04
    _MONTH_REGISTER = 0x05
    _YEAR_REGISTER = 0x06
    _REG_CONTROL = 0x07

    def __init__(self, port=I2C_PORT, addr=DS3231ADDR, at24c32_addr=AT24C32ADDR):
        """
        ???
        """
        self._bus = smbus.SMBus(port) #valid ports are 0 and 1
        self._addr = addr
        self._at24c32_addr = at24c32_addr

    ###########################
    # DS3231 real time clock functions
    ###########################
   def _write(self, register, data):
        """
        ???
        """
        self._bus.write_byte_data(self._addr, register, data)

    def _read(self, data):
        """
        ???
        """
        return self._bus.read_byte_data(self._addr, data)

    def _read_seconds(self):
        """
        ???
        """
        return _bcd_to_int(self._read(self._SECONDS_REGISTER) & 0x7F)   # wipe out the oscillator on bit

    def _read_minutes(self):
        """
        ???
        """
        return _bcd_to_int(self._read(self._MINUTES_REGISTER))

    def _read_hours(self):
        """
        ???
        """
        tmp = self._read(self._HOURS_REGISTER)
        if tmp == 0x64:
            tmp = 0x40
        return _bcd_to_int(tmp & 0x3F)

    def _read_day(self):
        """
        ???
        """
        return _bcd_to_int(self._read(self._DAY_OF_WEEK_REGISTER))

    def _read_date(self):
        """
        ???
        """
        return _bcd_to_int(self._read(self._DAY_OF_MONTH_REGISTER))

    def _read_month(self):
        """
        ???
        """
        return _bcd_to_int(self._read(self._MONTH_REGISTER))

    def _read_year(self):
        """
        ???
        """
        return _bcd_to_int(self._read(self._YEAR_REGISTER))

    def read_all(self):
        """
        Return a tuple such as (year, month, daynum, dayname, hours, minutes, seconds).
        """
        return (self._read_year(), self._read_month(), self._read_date(),
                self._read_day(), self._read_hours(), self._read_minutes(),
                self._read_seconds())

    def read_str(self):
        """
        Return a string such as 'YY-DD-MMTHH-MM-SS'.
        """
        return '%02d-%02d-%02dT%02d:%02d:%02d' % (self._read_year(),
                self._read_month(), self._read_date(), self._read_hours(),
                self._read_minutes(), self._read_seconds())

    def read_datetime(self, century=21, tzinfo=None):
        """
        Return the datetime.datetime object.
        """
        return datetime((century - 1) * 100 + self._read_year(),
                self._read_month(), self._read_date(), self._read_hours(),
                self._read_minutes(), self._read_seconds(), 0, tzinfo=tzinfo)

    def write_all(self, seconds=None, minutes=None, hours=None, day_of_week=None,
            day_of_month=None, month=None, year=None):
        """
        Direct write each user specified value.
        Range: seconds [0,59], minutes [0,59], hours [0,23],
                 day_of_week [0,7], day_of_month [1-31], month [1-12], year [0-99].
        """
        if seconds is not None:
            if seconds < 0 or seconds > 59:
                raise ValueError('Seconds is out of range [0,59].')
            seconds_reg = _int_to_bcd(seconds)
            self._write(self._SECONDS_REGISTER, seconds_reg)

        if minutes is not None:
            if minutes < 0 or minutes > 59:
                raise ValueError('Minutes is out of range [0,59].')
            self._write(self._MINUTES_REGISTER, _int_to_bcd(minutes))

        if hours is not None:
            if hours < 0 or hours > 23:
                raise ValueError('Hours is out of range [0,23].')
            self._write(self._HOURS_REGISTER, _int_to_bcd(hours)) # not  | 0x40 according to datasheet

        if year is not None:
            if year < 0 or year > 99:
                raise ValueError('Years is out of range [0, 99].')
            self._write(self._YEAR_REGISTER, _int_to_bcd(year))

        if month is not None:
            if month < 1 or month > 12:
                raise ValueError('Month is out of range [1, 12].')
            self._write(self._MONTH_REGISTER, _int_to_bcd(month))

        if day_of_month is not None:
            if day_of_month < 1 or day_of_month > 31:
                raise ValueError('Day_of_month is out of range [1, 31].')
            self._write(self._DAY_OF_MONTH_REGISTER, _int_to_bcd(day_of_month))

        if day_of_week is not None:
            if day_of_week < 1 or day_of_week > 7:
                raise ValueError('Day_of_week is out of range [1, 7].')
            self._write(self._DAY_OF_WEEK_REGISTER, _int_to_bcd(day_of_week))

    def write_datetime(self, dtime):
        """
        Write from a datetime.datetime object.
        """
        self.write_all(dtime.second, dtime.minute, dtime.hour,
                dtime.isoweekday(), dtime.day, dtime.month, dtime.year % 100)

    def write_system_datetime_now(self):
        """
        shortcut version of "DS3231.write_datetime(datetime.datetime.now())".
        """
        self.write_datetime(datetime.now())
        
    ###########################
    # SDL_DS3231 module onboard temperature sensor
    ###########################

    def get_temp(self):
        """
        ???
        """
        byte_tmsb = self._bus.read_byte_data(self._addr, 0x11)
        byte_tlsb = bin(self._bus.read_byte_data(self._addr, 0x12))[2:].zfill(8)
        return byte_tmsb + int(byte_tlsb[0]) * 2 ** (-1) + int(byte_tlsb[1]) * 2 ** (-2)

    ###########################
    # AT24C32 non-volatile ram Code
    ###########################

    def set_current_at24c32_address(self, address):
        """
        ???
        """
        addr1 = address / 256
        addr0 = address % 256
        self._bus.write_i2c_block_data(self._at24c32_addr, addr1, [addr0])

    def read_at24c32_byte(self, address):
        """
        ???
        """
        self.set_current_at24c32_address(address)
        return self._bus.read_byte(self._at24c32_addr)

    def write_at24c32_byte(self, address, value):
        """
        ???
        """
        addr1 = address / 256
        addr0 = address % 256
        self._bus.write_i2c_block_data(self._at24c32_addr, addr1, [addr0, value])
        time.sleep(0.20)
