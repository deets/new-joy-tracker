# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.

from setup import main

try:
    main()
except KeyboardInterrupt:
    import newjoy
    newjoy.deinit()
