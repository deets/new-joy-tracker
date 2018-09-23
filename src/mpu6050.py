# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import newjoy

MPU6050_ADDRESS_AD0_LOW               = 0x68
MPU6050_RA_WHO_AM_I                   = 0x75

def read_byte(bus, address, register):
    buffer = bytearray(1)
    bus.readfrom_mem_into(address, register, buffer)
    return buffer[0]


def present_on_bus(i2c):
    addresses = i2c.scan()
    if MPU6050_ADDRESS_AD0_LOW in addresses:
        print("is in addresses")
        res = read_byte(i2c, MPU6050_ADDRESS_AD0_LOW, MPU6050_RA_WHO_AM_I)
        print(res)
        if res == MPU6050_ADDRESS_AD0_LOW:
            return True
    return False


def register_on_protocol(i2c, protocol):
    protocol.register_task(i2c, newjoy.TASK_MPU6050, newjoy.MPU6050_BUFFER_SIZE)
