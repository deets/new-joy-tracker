#!/usr/bin/env python3
# -*- mode: python -*-
import sys
import serial
import argparse
from common import (
    DEFAULT_SERIAL_PORT,
    DEFAULT_BAUD,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        default=DEFAULT_SERIAL_PORT,
    )
    parser.add_argument(
        "--baud",
        default=DEFAULT_BAUD,
    )
    opts = parser.parse_args()
    p = serial.Serial(
        opts.port,
        opts.baud,
    )
    while True:
        count = p.inWaiting()
        if count:
            data = p.read(count)
            sys.stdout.buffer.write(data)


if __name__ == '__main__':
    main()
