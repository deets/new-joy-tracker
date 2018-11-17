# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.

def read_byte(bus, address, register):
    buffer = bytearray(1)
    bus.readfrom_mem_into(address, register, buffer)
    return buffer[0]
