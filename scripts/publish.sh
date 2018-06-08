#!/bin/bash
set -x
for fname in `dirname $0`/../src/*.py
do
    echo "publishing $fname"
    ampy --port /dev/ttyUSB0 put $fname
done
