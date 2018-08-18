# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import time
import ustruct
import array

class Protocol:

    FORMAT = "<IHIIIfffhfff" # NAME, SEQUENCE, TIMESTAMP, TEMPERATURE, PRESSURE,
                             # ACC_X, ACC_Y, ACC_Z, TEMP, GYR_X, GYR_Y, GYR_Z

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
        # startchar + datagram + checksum
        self.buffer = bytearray(ustruct.calcsize(self.FORMAT) + 2)
        self._count = 0
        self.bmp_data = array.array("i", [0, 0, 0])



    def read_sensors(self, pressure_sensor, mpu):
        acc_x, acc_y, acc_z, temp, gyr_x, gyr_y, gyr_z = mpu.read_sensors_scaled()

        if pressure_sensor is not None:
            pressure_sensor.read_compensated_data(self.bmp_data)
        else:
            self.bmp_data[0] = 0
            self.bmp_data[1] = 0
            self.bmp_data[2] = 0

        ustruct.pack_into(
            self.FORMAT,
            self.buffer, 1,
            self._name,
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
