#!/bin/bash
if [ $# == 1 ]; then
    PORT=$1
elif [ -e /dev/tty.SLAB_USBtoUART ]; then
    PORT=/dev/tty.SLAB_USBtoUART
else
    PORT=/dev/ttyUSB0
fi
screen $PORT 460800
