#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3.7
# -*- mode: python -*-
import os
import math
from functools import partial

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl

import PyQt5.QtWidgets as QtWidgets

from .three_d import QuaternionRep
from .processor import QuaternionProcessor
from .osc import OSCWorker, FileOSCWorker
from .common import angle_between_quats
from .windowmanager import WindowManager


class QuaternionInvestigator(QtCore.QObject):

    quaternion = QtCore.pyqtSignal(
      str, int, QtGui.QQuaternion,
      name="quaternion",
    )
    new_path = QtCore.pyqtSignal(str, name="new_path")
    reset = QtCore.pyqtSignal(str, name="reset")

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
        self.reset.connect(self._osc_worker.reset)  # just forward

    def about_to_quit(self):
        self._osc_worker.quit()

    def _got_osc(self, message):
        try:
            path, sensor_no, uptime, q1, q2, q3, q4, *_ = message
        except ValueError:
            pass
        else:
            if (path, sensor_no) not in self._quaternion_reps:
                self.add_quaternion_rep(path, sensor_no)
            quat = QtGui.QQuaternion(q1, q2, q3, q4)
            self._quaternion_reps[(path, sensor_no)].update(quat)
            self.quaternion.emit(path, sensor_no, quat)

    def add_quaternion_rep(self, path, sensor_no):
        self._quaternion_reps[(path, sensor_no)] = QuaternionRep(
          self.widget, path, sensor_no,
        )


class AnglePlot(QtCore.QObject):

    PEN_COLOR = (255, 0, 0)

    def __init__(self):
        super().__init__()
        self.widget = pg.PlotWidget(name='Angle Plot')
        self._curve = self.widget.plot()
        self._curve.setPen(self.PEN_COLOR)
        self._data = []
        self._curve.setData(self._data)
        self._a, self._b = None, None
        self._quaternions = {}

    def update(self, sensor_no, quaternion):
        self._quaternions[sensor_no] = quaternion
        quat_a = self._quaternions.get(self._a)
        quat_b = self._quaternions.get(self._b)
        if quat_a is not None and quat_b is not None:
            self._data.append(angle_between_quats(quat_a, quat_b))
            self._curve.setData(self._data)

    def update_indices(self, a, b):
        old = self._a, self._b
        self._a = a
        self._b = b
        if old != (a, b):
            self._data = []
            self._curve.setData(self._data)


class SourceSelection(QtCore.QAbstractListModel):

    indices = QtCore.pyqtSignal(int, int, name="indices")

    def __init__(self):
        super().__init__()
        self._data = [
        ]

        w = self.widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        w.setLayout(layout)

        self._source_a = QtWidgets.QComboBox()
        self._source_b = QtWidgets.QComboBox()
        self._source_a.setModel(self)
        self._source_b.setModel(self)
        self._source_a.currentIndexChanged.connect(self._index_changed)
        self._source_b.currentIndexChanged.connect(self._index_changed)

        layout.addWidget(self._source_a)
        layout.addWidget(self._source_b)

    def _index_changed(self, _index):
        self.indices.emit(
            self._source_a.currentData(),
            self._source_b.currentData(),
        )

    def data(self, index, role):
        if index.row() < len(self._data):
            return self._data[index.row()]
        return QtCore.QVariant()

    def rowCount(self, _parent):
        return len(self._data)

    def add_source(self, source):
        self.beginInsertRows(
            QtCore.QModelIndex(),
            len(self._data), len(self._data)
        )
        self._data.append(source)
        self.endInsertRows()


class ResetController(QtCore.QObject):

    reset = QtCore.pyqtSignal(str, name="reset")

    def __init__(self):
        super().__init__()
        w = self.widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        w.setLayout(layout)

        self._dest = QtWidgets.QComboBox()
        self._reset = QtWidgets.QPushButton("Reset!")
        layout.addWidget(self._dest)
        layout.addWidget(self._reset)
        self._reset.clicked.connect(self.send_reset)

    def add_new_path(self, path):
        self._dest.addItem(path)

    def send_reset(self):
        if self._dest.currentText():
            self.reset.emit(self._dest.currentText())


def main():
    app = QtGui.QApplication([])
    wm = WindowManager()

    osc_worker = FileOSCWorker(os.path.expanduser("~/osc-shark-export-2"))
    qi = QuaternionInvestigator(osc_worker)

    three_d_window = QtGui.QMainWindow()
    three_d_window.setObjectName("three_d_window")
    three_d_window.setWindowTitle('Quaternion Investigator')
    three_d_window.setCentralWidget(qi.widget)
    three_d_window.show()
    wm += three_d_window

    # mw = QtGui.QMainWindow()
    # mw.setWindowTitle('Quaternion Investigator')
    # cw = QtGui.QWidget()
    # mw.setCentralWidget(cw)
    # layout = QtGui.QVBoxLayout()
    # cw.setLayout(layout)

    # reset_controller = ResetController()
    # qp = QuaternionProcessor()

    # angle_plot = AnglePlot()
    # source_selection = SourceSelection()
    # source_selection.indices.connect(angle_plot.update_indices)

    # qi.quaternion_rep_added.connect(source_selection.add_source)
    # qi.quaternion.connect(angle_plot.update)
    # qi.quaternion.connect(qp.update)
    # qi.new_path.connect(reset_controller.add_new_path)
    # reset_controller.reset.connect(qi.reset)

    # layout.addWidget(reset_controller.widget)
    # layout.addWidget(source_selection.widget)
    # layout.addWidget(angle_plot.widget)
    # mw.show()

    wm.load_window_settings()
    app.aboutToQuit.connect(wm.save_window_settings)
    app.aboutToQuit.connect(qi.about_to_quit)
    for w in [three_d_window]:
        w.raise_()

    app.exec_()


if __name__ == '__main__':
    main()
