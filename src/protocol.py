# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import time
import ustruct
import array
import machine

class Protocol:

    FORMAT = "<HIIIfffhfff" # SEQUENCE, TIMESTAMP, TEMPERATURE, PRESSURE,
                             # ACC_X, ACC_Y, ACC_Z, TEMP, GYR_X, GYR_Y, GYR_Z

    def __init__(self):
        name = machine.unique_id()
        assert len(name) == 6
        # startchar + datagram + checksum + name
        self.buffer = bytearray(ustruct.calcsize(self.FORMAT) + 2 + 6)
        for i, c in enumerate(name):
            self.buffer[1 + i] = c # copy over name
        self._count = 0
        self.bmp_data = array.array("i", [0, 0, 0])


    def read_sensors(self, pressure_sensor, mpu):
        if mpu is not None:
            acc_x, acc_y, acc_z, temp, gyr_x, gyr_y, gyr_z = mpu.read_sensors_scaled()
        else:
            acc_x, acc_y, acc_z, temp, gyr_x, gyr_y, gyr_z = 0, 0, 0, 0, 0, 0, 0

        if pressure_sensor is not None:
            pressure_sensor.read_compensated_data(self.bmp_data)
        else:
            self.bmp_data[0] = 0
            self.bmp_data[1] = 0
            self.bmp_data[2] = 0

        ustruct.pack_into(
            self.FORMAT,
            self.buffer, 1 + 6, # start-byte plus name
            self._count,
            time.ticks_ms(),
            self.bmp_data[0],
            self.bmp_data[1],
            acc_x, acc_y, acc_z,
            temp,
            gyr_x, gyr_y, gyr_z,
        )
        self.buffer[0] = ord('#')
        self.buffer[-1] = sum(self.buffer[1:-1]) & 0xff
        self._count += 1
