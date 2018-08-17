# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import time
import ustruct

class Protocol:

    FORMAT = "<IHIII" # NAME, SEQUENCE, TIMESTAMP, TEMPERATURE, PRESSURE

    def __init__(self, name):
        """
        name must be a four-character name that identifies
        the device. Fill with \0 to pad, e.g

        BOB\0
        EVE\0
        ANNA
        DIEZ

        """
        assert len(name) == 4
        self._name = ustruct.unpack("<I", ustruct.pack("ssss", *name))[0]
        self.buffer = bytearray(ustruct.calcsize(self.FORMAT))
        self._count = 0


    def message(self, temperature, pressure):
        ustruct.pack_into(
            self.FORMAT,
            self.buffer, 0,
            self._name,
            self._count,
            time.ticks_ms(),
            temperature,
            pressure,
        )
        self._count += 1
