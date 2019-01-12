# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import utime


def read_byte(bus, address, register):
    buffer = bytearray(1)
    bus.readfrom_mem_into(address, register, buffer)
    return buffer[0]


TIMESTAMPS = {}

def measure(text):
    def _d(func):
        def _w(*a, **kw):
            try:
                then = utime.ticks_us()
                return func(*a, **kw)
            finally:
                elapsed = utime.ticks_diff(utime.ticks_us(), then)
                TIMESTAMPS[text] = elapsed
        return _w
    return _d


def print_measurements():
    for key, value in TIMESTAMPS.items():
        print(key, value)


def cycle():
    i = 0
    while True:
        yield i
        i += 1
