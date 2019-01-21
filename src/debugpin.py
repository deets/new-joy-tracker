import machine


BOOT_PIN = 0
DEBUG_MODE = False


def toggle_debug(pin):
    global DEBUG_MODE, SPOKE_MAX_TS_DELTAS
    DEBUG_MODE = not DEBUG_MODE
    SPOKE_MAX_TS_DELTAS = {}


def setup():
    p = machine.Pin(
        BOOT_PIN,
        machine.Pin.IN,
        machine.Pin.PULL_UP,
    )
    p.irq(trigger=machine.Pin.IRQ_FALLING, handler=toggle_debug)
