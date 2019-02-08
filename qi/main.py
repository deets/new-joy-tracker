#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3.7
# -*- mode: python -*-
import os
import sys
from functools import partial

from pyqtgraph.Qt import QtCore, QtGui

import pyqtgraph.opengl as gl

from .three_d import QuaternionRep
from .processor import QuaternionProcessor
from .osc import OSCWorker, FileOSCWorker
from .windowmanager import WindowManager
from .insights import setup_window_for_path


class QuaternionInvestigator(QtCore.QObject):

    quaternion = QtCore.pyqtSignal(
      str, int, QtGui.QQuaternion,
      name="quaternion",
    )
    acceleration = QtCore.pyqtSignal(
        str, int, float, float, name="acceleration",
    )
    new_path = QtCore.pyqtSignal(str, name="new_path")
    reset = QtCore.pyqtSignal(str, name="reset")
    update_mask = QtCore.pyqtSignal(str, int, name="update_mask")

    def __init__(self, osc_worker):
        super().__init__()
        self.widget = w = gl.GLViewWidget()
        w.setCameraPosition(distance=40)
        w.show()
        g = gl.GLGridItem()
        g.scale(2, 2, 1)
        w.addItem(g)

        self._quaternion_reps = {}

        self._osc_worker = osc_worker
        self._osc_worker.message.connect(self._got_osc)
        self._osc_worker.new_path.connect(self.new_path)  # just forward
        self.reset.connect(lambda path: self._osc_worker.reset(path))
        self.update_mask.connect(
          lambda path, mask: self._osc_worker.update_mask(path, mask),
        )
        self._osc_worker.start()

    def about_to_quit(self):
        self._osc_worker.quit()

    def _got_osc(self, message):
        try:
            path, sensor_no, uptime, q1, q2, q3, q4, acc, acc_f = message
        except ValueError:
            pass
        else:
            if (path, sensor_no) not in self._quaternion_reps:
                self.add_quaternion_rep(path, sensor_no)
            quat = QtGui.QQuaternion(q1, q2, q3, q4)
            self._quaternion_reps[(path, sensor_no)].update(quat)
            self.quaternion.emit(path, sensor_no, quat)
            self.acceleration.emit(path, sensor_no, acc, acc_f)

    def add_quaternion_rep(self, path, sensor_no):
        self._quaternion_reps[(path, sensor_no)] = QuaternionRep(
          self.widget, path, sensor_no,
        )


def main():
    app = QtGui.QApplication([])
    wm = WindowManager()

    if len(sys.argv) == 2:
        osc_worker = FileOSCWorker(os.path.expanduser(sys.argv[1]))
    else:
        osc_worker = OSCWorker("", 10000)
    qi = QuaternionInvestigator(osc_worker)

    three_d_window = QtGui.QMainWindow()
    three_d_window.setObjectName("three_d_window")
    three_d_window.setWindowTitle('Quaternion Investigator')
    three_d_window.setCentralWidget(qi.widget)
    three_d_window.show()
    wm += three_d_window

    qi.new_path.connect(partial(setup_window_for_path, wm, qi))

    wm.load_window_settings()
    app.aboutToQuit.connect(wm.save_window_settings)
    app.aboutToQuit.connect(qi.about_to_quit)
    for w in [three_d_window]:
        w.raise_()

    app.exec_()


if __name__ == '__main__':
    main()
