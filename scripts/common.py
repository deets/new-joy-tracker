import platform

DEFAULT_SERIAL_PORT = "/dev/tty.SLAB_USBtoUART" if \
    platform.system() == 'Darwin' else "/dev/ttyUSB0"

DEFAULT_BAUD = 260400
