#!/bin/bash
if [ $# == 1 ]; then
    PORT=$1
elif [ -e /dev/tty.SLAB_USBtoUART ]; then
    PORT=/dev/tty.SLAB_USBtoUART
else
    PORT=/dev/ttyUSB0
fi

if [ $# == 2]; then
    BAUD=$2
else
    BAUD=460800
fi
screen $PORT $BAUD
