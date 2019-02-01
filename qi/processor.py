# -*- coding: utf-8 -*-
# Copyright: 2019, Diez B. Roggisch, Berlin . All rights reserved.
import rx

from pyqtgraph.Qt import QtCore

class QuaternionProcessor(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def update(self, sensor_no, quat):
        pass # print(sensor_no, quat)
