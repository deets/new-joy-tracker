# -*- coding: utf-8 -*-
# Copyright: 2019, Diez B. Roggisch, Berlin . All rights reserved.
import utime
from micropython import const
# from machine import Pin, SPI
from nrf24l01 import (
#     NRF24L01,
    START_LISTENING_TIMEOUT_US,
#     POWER_0,
#     POWER_3,
#     SPEED_2M,
#     SPEED_250K,
#     OBSERVE_TX,
)
from names import get_pipe_id
from misc import measure, print_measurements, cycle
import newjoy

PIN_CFG = {
    'miso': 22,
    'mosi': 23,
    'sck': 18,
    'csn': 5,
    'ce': 19
}
CHANNEL = const(124)
# POWER = POWER_3
# SPEED = SPEED_2M
# timeout until we don't wait for a
# spoke's response in ms
RECEIVE_TIMEOUT_MS = const(100)
# timeout to wait before sending in us. This
# gives the hub time to switch to RX
# The minimum is the START_LISTENING_TIMEOUT_US
TX_SWITCH_DELAY_US = START_LISTENING_TIMEOUT_US + const(500)


def ping(spoke):
    error = newjoy.nrf24_send(b"PING")
    if error != 1:
        return False
    return True


def receive(spoke):
    packets = []
    while True:
        start_time = utime.ticks_ms()
        while not newjoy.nrf24_any():
            if utime.ticks_diff(utime.ticks_ms(), start_time) > \
               RECEIVE_TIMEOUT_MS:
                return
        packet = newjoy.nrf24_recv()
        packets.append(packet[2:2 + packet[1]])
        if not packet[0]:
            break
    return b"".join(packets)


@measure("hub_work_in_py")
def hub_work_in_py(spoke):
    newjoy.nrf24_open_rx_pipe(1, get_pipe_id(spoke))

    if ping(spoke):
        newjoy.nrf24_start_listening()
        try:
            answer = receive(spoke)
        finally:
            newjoy.nrf24_stop_listening()
        if answer is None:
            print('failed, response timed out')
            return 1
        else:
            print(answer)
            # only successful branch!
            return 0
    else:
        return 1


def hub_work_in_c(spoke):
    try:
        message = newjoy.nrf24_hub_to_spoke(get_pipe_id(spoke))
        print(message)
    except OSError as e:
        print(e)
        return 1
    return 0


WORK_IN_C = False


def hub(spokes):
    newjoy.nrf24_teardown()
    # we transmit using our ID
    newjoy.nrf24_setup(get_pipe_id())
    failures = 0
    for i in cycle():
        # # in this special case, we need to
        # # sleep because the receiver is switching
        # # back
        # if len(spokes) == 1:
        #     utime.sleep_us(TX_SWITCH_DELAY_US * 10)
        for j, spoke in enumerate(spokes):
            print("----------", i, j, failures)
            utime.sleep_ms(2000)
            print("ping")
            if WORK_IN_C:
                failures += hub_work_in_c(spoke)
            else:
                failures += hub_work_in_py(spoke)
