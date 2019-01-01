# -*- coding: utf-8 -*-
# Copyright: 2019, Diez B. Roggisch, Berlin . All rights reserved.
import utime
from micropython import const
from machine import Pin, SPI
from nrf24l01 import (
    NRF24L01,
    START_LISTENING_TIMEOUT_US,
    POWER_0,
    POWER_3,
    SPEED_2M,
    SPEED_250K,
    )
from names import get_pipe_id

PIN_CFG = {
    'miso': 22,
    'mosi': 23,
    'sck': 18,
    'csn': 5,
    'ce': 19
}
CHANNEL = const(46)
POWER = POWER_3
SPEED = SPEED_250K
# timeout until we don't wait for a
# spoke's response in ms
RECEIVE_TIMEOUT_MS = const(25)
# timeout to wait before sending in us. This
# gives the hub time to switch to RX
# The minimum is the START_LISTENING_TIMEOUT_US
TX_SWITCH_DELAY_US = START_LISTENING_TIMEOUT_US + const(500)


def create_nrf():
    csn = Pin(PIN_CFG['csn'], mode=Pin.OUT, value=1)
    ce = Pin(PIN_CFG['ce'], mode=Pin.OUT, value=0)
    spi = SPI(
        -1,
        sck=Pin(PIN_CFG['sck']),
        mosi=Pin(PIN_CFG['mosi']),
        miso=Pin(PIN_CFG['miso']),
    )
    nrf = NRF24L01(
        spi,
        csn,
        ce,
        payload_size=4,
        channel=CHANNEL,
    )
    nrf.set_power_speed(POWER, SPEED)
    return nrf


def send_and_receive(spoke, nrf):
    nrf.open_rx_pipe(1, get_pipe_id(spoke))
    nrf.send(b"PING")
    nrf.start_listening()
    # wait for response, with timeout
    start_time = utime.ticks_ms()
    try:
        while not nrf.any():
            if utime.ticks_diff(utime.ticks_ms(), start_time) > \
               RECEIVE_TIMEOUT_MS:
                print('failed, response timed out')
                return
        return nrf.recv()
    finally:
        nrf.stop_listening()


def hub(spokes):
    N = 100
    failures = 0
    timeouts = 0
    max_elapsed = 0
    avg_elapsed = 0.0
    nrf = create_nrf()
    # we transmit using our ID
    nrf.open_tx_pipe(get_pipe_id())
    while True:
        for spoke in spokes:
            then = utime.ticks_us()
            try:
                message = send_and_receive(spoke, nrf)
                elapsed = utime.ticks_diff(utime.ticks_us(), then)
                max_elapsed = max(max_elapsed, elapsed)
                if message is not None:

                    avg_elapsed -= avg_elapsed / N
                    avg_elapsed += elapsed / N
                    print("MSG:", message, max_elapsed, avg_elapsed)
                else:
                    timeouts += 1
                    print("timeouts: ", timeouts)
            except OSError:
                failures += 1
                print("failures: ", failures)



def spoke(hub):
    nrf = create_nrf()
    # we transmit using our ID
    nrf.open_tx_pipe(get_pipe_id())
    nrf.open_rx_pipe(1, get_pipe_id(hub))
    nrf.start_listening()
    while True:
        if nrf.any():
            # receive potentially
            # sereval messages. This
            # should not happen but
            # if so, just assume we're supposed
            # to send afterwards
            while nrf.any():
                buf = nrf.recv()
                #print("MSG:", buf)
            utime.sleep_us(TX_SWITCH_DELAY_US)
            nrf.stop_listening()
            try:
                nrf.send("PONG")
            except OSError:
                print(".")
            nrf.start_listening()
