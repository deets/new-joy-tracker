# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.

import machine
import time
import socket
import mpu6050
import bme280

from protocol import Protocol
from names import get_name
from nrf24protocol import spoke_setup, spoke_wait, spoke_send, hub

# I2C 1 is missing due to some
# system setup issue when the lines
# pulled up.
#
# Looking from the top of the PCB
# with the ESP32 module pointing
# towards you (USB port!),
# this is the allocation of I2C busses:
#
#    +------------+
#    |            |
#    | [NC]  [ 2] |
#    |            |
#    | [ 0]  [ 3] |
#    |            |
#    | +---+      |
#    | |   |      |
#    | |   |      |
#    | +USB+      |
#    +------------+
#
# define busno, SCL, SDA
I2C_BUSSES = [
   (0, (27, 26)),  # I2C 0 on PCB
   (2, (4, 0)),    # I2C 2 on PCB
   (3, (17, 16)),  # I2C 3 on PCB
]

CLK = 18  # SPI bus for 24L01
MOSI = 23
MISO = 22
CS0 = 5
CE = 19  # chip enable for 24L01
IRQ = 21

PORT = 5000
OSC_PORT = 10000
CONNECT_TIMEOUT = 100
RESET_COUNT = 10  # after these, we try to reset the board for reconnection
LOOP_SLEEP_MS = 70
SENSOR_PERIOD = 2  # in milliseconds
I2C_FREQUENCY = 1000_000

# The known spokes
SPOKES = [
    "OTTO",
    "IRIS",
]
HUB_NAME = "TIMO"


def setup_i2c_busses():
    for busno, (scl, sda) in I2C_BUSSES:
        scl = machine.Pin(scl, machine.Pin.OUT)
        sda = machine.Pin(sda, machine.Pin.OUT)
        yield busno, machine.I2C(freq=I2C_FREQUENCY, scl=scl, sda=sda)


def setup_socket(nic):
    while not nic.isconnected():
        time.sleep(.1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock


def setup_all():
    protocol = Protocol()
    for busno, i2c in setup_i2c_busses():
        print("scanning bus", i2c)
        for address in mpu6050.present_on_bus(i2c):
            print("found mpu @{}:{}, registering with protocol".format(
                busno,
                address,
                )
            )
            mpu6050.register_on_protocol(i2c, address, protocol, busno)
        for address in bme280.present_on_bus(i2c):
            print("found bmp280 @{}:{}, registering with protocol".format(
                busno,
                address,
                )
            )
            bme280.register_on_protocol(i2c, address, protocol, busno)

    protocol.assemble(SENSOR_PERIOD)
    return protocol



def main():
    name = get_name()
    print("*** {} ***".format(name))
    if name == HUB_NAME:
        hub(SPOKES)

    protocol = setup_all()
    spoke_setup(HUB_NAME)
    while True:
        if spoke_wait():
            print(".", end="")
            spoke_send(protocol.update())
        machine.idle()
