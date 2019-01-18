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

DEBUG_MODE = False


def hub_work_in_c(spoke):
    try:
        message = newjoy.nrf24_hub_to_spoke(get_pipe_id(spoke))
        if not DEBUG_MODE:
            sys.stdout.write(message)
    except OSError as e:
        if DEBUG_MODE:
            print(spoke, e)
        return 1
    return 0


def toggle_debug(pin):
    global DEBUG_MODE
    DEBUG_MODE = not DEBUG_MODE


def setup_debug_toggle():
    p = machine.Pin(
        BOOT_PIN,
        machine.Pin.IN,
        machine.Pin.PULL_UP,
    )
    p.irq(trigger=machine.Pin.IRQ_FALLING, handler=toggle_debug)


def hub(spokes):
    setup_debug_toggle()
    newjoy.nrf24_teardown()
    # we transmit using our ID
    newjoy.nrf24_setup(get_pipe_id())
    failures = 0
    for i in cycle():
        for spoke in spokes:
            if DEBUG_MODE:
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
