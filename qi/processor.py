# -*- coding: utf-8 -*-
# Copyright: 2019, Diez B. Roggisch, Berlin . All rights reserved.
import rx.subjects
from pyqtgraph.Qt import QtCore

from .common import angle_between_quats


class QuaternionProcessor(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self._subjects = {}

    def update(self, sensor_no, quat):
        if sensor_no not in self._subjects:
            s = self._subjects[sensor_no] = rx.subjects.Subject()
            s.pairwise().map(lambda qs: angle_between_quats(*qs)).subscribe(
                lambda value: print("Angle: {0}".format(value)))

        self._subjects[sensor_no].on_next(quat)
