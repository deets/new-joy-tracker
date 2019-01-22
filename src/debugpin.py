import machine
import newjoy

BOOT_PIN = 0
DEBUG_MODE = False


def toggle_debug(pin):
    global DEBUG_MODE, SPOKE_MAX_TS_DELTAS
    DEBUG_MODE = not DEBUG_MODE
    SPOKE_MAX_TS_DELTAS = {}
    # print()
    # for i in range(newjoy.task_count()):
    #     print(i, newjoy.task_info(i))
    # print()


def setup():
    p = machine.Pin(
        BOOT_PIN,
        machine.Pin.IN,
        machine.Pin.PULL_UP,
    )
    p.irq(trigger=machine.Pin.IRQ_FALLING, handler=toggle_debug)
