# -*- coding: utf-8 -*-
# Copyright: 2019, Diez B. Roggisch, Berlin . All rights reserved.
import argparse
import logging
import platform

DEFAULT_SERIAL_PORT = "/dev/tty.SLAB_USBtoUART" if \
    platform.system() == 'Darwin' else "/dev/ttyUSB0"

DEFAULT_BAUD = 460800


def core_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    return parser


def core_app_setup(opts):
    logging.basicConfig(
        level=logging.DEBUG if opts.debug else logging.INFO,
    )
