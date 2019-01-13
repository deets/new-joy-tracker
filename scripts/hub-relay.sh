#!/usr/bin/env python3.6
# -*- mode: python -*-
import sys
import serial

BAUD = 460800


p = serial.Serial(
    sys.argv[1],
    BAUD,
)


class HubDecoder:

    def __init__(self):
        self._buffer = b''


    def feed(self, bytestring):

while True:
    count = p.inWaiting()
    if count:
        print(p.read(count))
