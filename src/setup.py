import machine
import time
import socket

import array
import ustruct

from wifi import setup_wifi

I2C_BUSSES = [
    # SCL, SDA
    #(12, 14),
    (27, 26),
    (17, 16),
    (4, 0)
]

CLK = 18 # SPI bus for 24L01
MOSI = 23
MISO = 22
CS0 = 5
CE = 19 # chip enable for 24L01
IRQ = 21

PORT = 5000
CONNECT_TIMEOUT = 100
RESET_COUNT = 10 # after these, we try to reset the board for reconnection
LOOP_SLEEP_MS = 70
SENSOR_PERIOD = 2 # in milliseconds
I2C_FREQUENCY = 1000_000


def setup_i2c_busses():
    for scl, sda in I2C_BUSSES:
        scl = machine.Pin(scl, machine.Pin.OUT)
        sda = machine.Pin(sda, machine.Pin.OUT)
        yield machine.I2C(freq=I2C_FREQUENCY, scl=scl, sda=sda)


def setup_all():
    for i, i2c in enumerate(setup_i2c_busses()):
        print("scanning bus", i)
        print(i2c.scan())


def main():
    while True:
        setup_all()
        time.sleep(1)
