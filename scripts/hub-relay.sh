#!/usr/bin/env python3.6
# -*- code: python -*-
import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
    )
)

from newjoy.hub_relay import main
main()
