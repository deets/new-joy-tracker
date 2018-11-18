# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.

import machine
import time
import socket
import mpu6050
import bme280
from uosc.client import Client


from protocol import Protocol
from wifi import setup_wifi

I2C_BUSSES = [
    #define SCL, SDA
    (27, 26),
    (17, 16),
    (4, 0)
]

CLK = 18  # SPI bus for 24L01
MOSI = 23
MISO = 22
CS0 = 5
CE = 19  # chip enable for 24L01
IRQ = 21

PORT = 5000
CONNECT_TIMEOUT = 100
RESET_COUNT = 10  # after these, we try to reset the board for reconnection
LOOP_SLEEP_MS = 70
SENSOR_PERIOD = 2  # in milliseconds
I2C_FREQUENCY = 1000_000


def setup_i2c_busses():
    for scl, sda in I2C_BUSSES:
        scl = machine.Pin(scl, machine.Pin.OUT)
        sda = machine.Pin(sda, machine.Pin.OUT)
        yield machine.I2C(freq=I2C_FREQUENCY, scl=scl, sda=sda)


def setup_socket(nic):
    while not nic.isconnected():
        time.sleep(.1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock


def setup_all():
    protocol = Protocol()
    for busno, i2c in enumerate(setup_i2c_busses()):
        print("scanning bus", i2c)
        for address in mpu6050.present_on_bus(i2c):
            print("found mpu @{}:{}, registering with protocol".format(
                busno,
                address,
                )
            )
            mpu6050.register_on_protocol(i2c, address, protocol)
        for address in bme280.present_on_bus(i2c):
            print("found bmp280 @{}:{}, registering with protocol".format(
                busno,
                address,
                )
            )
            bme280.register_on_protocol(i2c, address, protocol)

    protocol.assemble(SENSOR_PERIOD)
    return protocol


def main():
    protocol = setup_all()

    while True:
        try:
            nic, destination_address = setup_wifi()
            break
        except Exception:
            pass

    reconnect_count = 0

    osc = Client(destination_address, 10000)

    while True:
        print("connecting...")
        try:
            s = setup_socket(nic)
            while True:
                protocol.update()
                s.sendto(protocol.buffer, (destination_address, PORT))
                protocol.send_osc(osc)
                time.sleep_ms(LOOP_SLEEP_MS)
                machine.idle()
        except OSError:
            reconnect_count += 1
            if reconnect_count > RESET_COUNT:
                print("resetting hard")
                machine.reset()
            time.sleep(1)
