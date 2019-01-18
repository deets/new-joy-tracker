# -*- coding: utf-8 -*-
# Copyright: 2019, Diez B. Roggisch, Berlin . All rights reserved.
import utime
import sys
import machine


import newjoy
from misc import cycle
from names import get_pipe_id


TX_SWITCH_DELAY_US = 150
BOOT_PIN = 0

WRITE_RAW = True


def hub_work_in_c(spoke):
    try:
        message = newjoy.nrf24_hub_to_spoke(get_pipe_id(spoke))
        if WRITE_RAW:
            sys.stdout.write(message)
    except OSError as e:
        print(spoke, e)
        return 1
    return 0


def toggle_raw(pin):
    global WRITE_RAW
    WRITE_RAW = not WRITE_RAW


def setup_raw_toggle():
    p = machine.Pin(
        BOOT_PIN,
        machine.Pin.IN,
        machine.Pin.PULL_UP,
    )
    p.irq(trigger=machine.Pin.IRQ_FALLING, handler=toggle_raw)


def hub(spokes):
    setup_raw_toggle()
    newjoy.nrf24_teardown()
    # we transmit using our ID
    newjoy.nrf24_setup(get_pipe_id())
    failures = 0
    for i in cycle():
        for spoke in spokes:
            if not WRITE_RAW:
                print(i, spoke)
                print(newjoy.nrf24_error_info())
            # # in this special case, we need to
            # # sleep because the receiver is switching
            # # back
            if len(spokes) == 1:
                utime.sleep_us(TX_SWITCH_DELAY_US)
            failures += hub_work_in_c(spoke)

def spoke_setup(hub):
    newjoy.nrf24_teardown()
    # we transmit using our ID
    spoke_id = get_pipe_id()
    newjoy.nrf24_setup(spoke_id)
    newjoy.nrf24_start_listening()


def spoke_wait():
    if newjoy.nrf24_any():
        while newjoy.nrf24_any():
            newjoy.nrf24_recv()
        return True
    return False


def spoke_send(buffer):
    newjoy.nrf24_spoke_to_hub_send(buffer)
