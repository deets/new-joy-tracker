# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.

import objc
from objc import IBAction
from Foundation import (
    NSObject,
    NSLog,
    )

from angelia.protocol import Hub

class ApplicationDelegate(NSObject):

    def init(self):
        self = super(ApplicationDelegate, self).init()
        self._hub = Hub()
        return self


    def applicationDidFinishLaunching_(self, _):
        NSLog("applicationDidFinishLaunching_")
        self._hub.start()

    def applicationWillTerminate_(self, sender):
        pass
