# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import ustruct

class Protocol:

    FORMAT = "<III"

    def __init__(self, name):
        assert len(name) == 4
        self._name = ustruct.unpack("<I", ustruct.pack("ssss", *name))[0]
        self._buffer = bytearray(ustruct.calcsize(self.FORMAT))


    def message(self, temperature, pressure):
        ustruct.pack_into(self.FORMAT, self._buffer, 0, self._name, temperature, pressure)
        return self._buffer
