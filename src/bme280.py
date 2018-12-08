# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import newjoy
from misc import read_byte

BME280_I2CADDR = 0x76
BMP280_ID = 0xD0


def present_on_bus(i2c):
    res = []
    addresses = i2c.scan()
    for address in (BME280_I2CADDR, BME280_I2CADDR + 1):
        if address in addresses:
            id_register = read_byte(i2c, address, BMP280_ID)
            if id_register == ord(b'X'):
                res.append(address)
    return res


def register_on_protocol(i2c, address, protocol, busno):
    protocol.register_task(
        i2c,
        address,
        newjoy.TASK_BMP280,
        newjoy.BMP280_BUFFER_SIZE,
        busno,
    )
