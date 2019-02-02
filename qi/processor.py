# -*- coding: utf-8 -*-
# Copyright: 2019, Diez B. Roggisch, Berlin . All rights reserved.
import rx.subjects
from pyqtgraph.Qt import QtCore

from .common import angle_between_quats


def angle_between_succesors(args):
    old, new = args
    return old[0], angle_between_quats(
        old[1], new[1],
    )


class QuaternionProcessor(QtCore.QObject):

    subsequent_angle = QtCore.pyqtSignal(
        int, float,
        name="subsequent_angle"
    )

    def __init__(self):
        super().__init__()
        self._subjects = {}

    def update(self, sensor_no, quat):
        if sensor_no not in self._subjects:
            s = self._subjects[sensor_no] = rx.subjects.Subject()
            subsequent_angle = s.pairwise().map(angle_between_succesors)
            subsequent_angle.subscribe(
                lambda value: print("Angle: {0}".format(value))
            )
            subsequent_angle.subscribe(
                lambda arg: self.subsequent_angle.emit(arg[0], arg[1])
            )

        self._subjects[sensor_no].on_next((sensor_no, quat))
