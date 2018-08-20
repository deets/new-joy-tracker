#!/bin/bash
if [ -e /dev/tty.SLAB_USBtoUART ]; then
    PORT=/dev/tty.SLAB_USBtoUART
else
    PORT=/dev/ttyUSB0
fi
screen $PORT 115200
