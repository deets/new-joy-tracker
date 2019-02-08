# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.

import machine
import uselect
import time
import socket
import mpu6050
import debugpin
from uosc.client import Client
from protocol import Protocol
from wifi import setup_wifi
from names import get_name

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
RESET_COUNT = 20  # after these, we try to reset the board for reconnection
WIFI_COOLDOWN_PHASE = 10 # number of seconds we wait for a really stable connection
LOOP_SLEEP_MS = 70
SENSOR_PERIOD = 5  # in milliseconds
I2C_FREQUENCY = 1000_000


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
        # for address in bme280.present_on_bus(i2c):
        #     print("found bmp280 @{}:{}, registering with protocol".format(
        #         busno,
        #         address,
        #         )
        #     )
        #     bme280.register_on_protocol(i2c, address, protocol, busno)

    protocol.assemble(SENSOR_PERIOD)
    return protocol


CONNECT_TO_NET = True
SETUP_DEBUG_PIN = False


def wait_while_idling(seconds):
    then = time.time() + seconds
    while then > time.time():
        machine.idle()


def main():
    if SETUP_DEBUG_PIN:
        debugpin.setup()
    name = get_name()
    print(name)
    protocol = setup_all()

    reconnect_count = 0
    osc_client = None
    nic, destination_address = None, None

    if CONNECT_TO_NET:
        while True:
            try:
                nic, destination_address = setup_wifi()
                break
            except Exception:
                pass

        osc_client = Client(destination_address, OSC_PORT)
        print("sending OSC to", destination_address, OSC_PORT)

    # we have a spurious boot pin trigger,
    # I force debug off once here
    debugpin.DEBUG_MODE = False
    poll = uselect.poll()
    while True:
        print("connecting...")
        wait_while_idling(WIFI_COOLDOWN_PHASE)
        try:
            # this is needed to open the socket
            osc_client.send("/IGNORE", 0)
            poll.register(osc_client.sock, uselect.POLLIN)
            while True:
                machine.idle()
                protocol.update()
                protocol.send_osc(osc_client)
                for sock, kind in poll.ipoll(LOOP_SLEEP_MS):
                    incoming = sock.recv(100)
                    protocol.process_incoming(incoming)
                if debugpin.DEBUG_MODE:
                    print(".", end="")
        except OSError:
            reconnect_count += 1
            if reconnect_count > RESET_COUNT:
                print("resetting hard")
                machine.reset()
            time.sleep(1)
