# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import newjoy

from misc import read_byte

MPU6050_ADDRESS_AD0_LOW = 0x68
MPU6050_RA_WHO_AM_I = 0x75
MPU6050_EXPECTED_IDS = (MPU6050_ADDRESS_AD0_LOW, 0x72)

def present_on_bus(i2c):
    res = []
    addresses = i2c.scan()
    for address in (MPU6050_ADDRESS_AD0_LOW, MPU6050_ADDRESS_AD0_LOW + 1):
        if address in addresses:
            id_register = read_byte(i2c, address, MPU6050_RA_WHO_AM_I)
            if id_register in MPU6050_EXPECTED_IDS:
                res.append(address)
    return res


def register_on_protocol(i2c, address, protocol, busno):
    protocol.register_task(
        i2c,
        address,
        newjoy.TASK_MPU6050,
        newjoy.MPU6050_BUFFER_SIZE,
        busno,
    )
