#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3.7
# -*- mode: python -*-
import sys
for p in [
        "/usr/local/Cellar/pyqt5/5.10.1_1/lib/python3.7/site-packages",
        "/usr/local/Cellar/sip/4.19.8_6/lib/python3.7/site-packages",
        ]:
    sys.path.append(p)


from functools import partial

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
import PyQt5.QtWidgets as QtWidgets

def debug_trace():
  from pdb import set_trace
  QtCore.pyqtRemoveInputHook()
  set_trace()


class QuaternionRep(QtCore.QObject):
    LENGTH = 3

    def __init__(self, w):
        super().__init__()

        self.quat = QtGui.QQuaternion()

        md = gl.MeshData.cylinder(
            rows=10,
            cols=20,
            radius=[.5, .5],
            length=self.LENGTH
        )
        colors = np.ones((md.faceCount(), 4), dtype=float)
        colors[::2, 0] = 0
        colors[:, 1] = np.linspace(0, 1, colors.shape[0])
        md.setFaceColors(colors)
        self._cylinder = gl.GLMeshItem(
            meshdata=md,
            smooth=True,
            drawEdges=True,
            edgeColor=(1, 0, 0, 1),
            shader='balloon',
        )
        w.addItem(self._cylinder)

    def rotate(self, angle):
        c = self._cylinder
        c.resetTransform()
        self.quat = QtGui.QQuaternion.fromAxisAndAngle(
            0, 1, 0, angle,
        )
        c.transform().rotate(self.quat)
        c.transform().translate(0, 0, -self.LENGTH / 2)


class QuaternionInvestigator(QtCore.QObject):

    angle = QtCore.pyqtSignal(float, name='angle')
    quaternion_rep_added = QtCore.pyqtSignal(int, name="quaternion_rep_added")

    def __init__(self):
        super().__init__()
        self._angle = 0.0

        self.widget = w = gl.GLViewWidget()
        w.setCameraPosition(distance=40)
        w.show()
        g = gl.GLGridItem()
        g.scale(2, 2, 1)
        w.addItem(g)

        self._quaternion_reps = {}

        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._update)
        self._timer.start(10)

    def _update(self):
        self._angle += 1  # degrees
        for qrep in self._quaternion_reps.values():
            qrep.rotate(self._angle)
        self.angle.emit(self._angle)

    def add_quaternion_rep(self, key):
        self._quaternion_reps[key] = QuaternionRep(self.widget)
        self.quaternion_rep_added.emit(key)


def save_window_settings(*windows):
    settings = QtCore.QSettings("deets_design", "quaternion-investigator")
    for i, window in enumerate(windows):
        settings.setValue("geometry-{}".format(i), window.saveGeometry())
        settings.setValue("windowState-{}".format(i), window.saveState())


def load_window_settings(*windows):
    settings = QtCore.QSettings("deets_design", "quaternion-investigator")
    for i, window in enumerate(windows):
        saved_geometry = settings.value("geometry-{}".format(i))
        if saved_geometry is not None:
            window.restoreGeometry(saved_geometry)
        saved_state = settings.value("windowState-{}".format(i))
        if saved_state is not None:
            window.restoreState(saved_state)


class AnglePlot(QtCore.QObject):

    PEN_COLOR = (255, 0, 0)

    def __init__(self):
        super().__init__()
        self.widget = pg.PlotWidget(name='Angle Plot')
        self._curve = self.widget.plot()
        self._curve.setPen(self.PEN_COLOR)
        self._data = []
        self._curve.setData(self._data)

    def update_data(self, angle):
        self._data.append(angle)
        self._curve.setData(self._data)


class SourceSelection(QtCore.QAbstractListModel):

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
        layout.addWidget(self._source_a)
        layout.addWidget(self._source_b)

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


def main():
    app = QtGui.QApplication([])

    mw = QtGui.QMainWindow()
    mw.setWindowTitle('Quaternion Investigator')
    cw = QtGui.QWidget()
    mw.setCentralWidget(cw)
    layout = QtGui.QVBoxLayout()
    cw.setLayout(layout)

    angle_plot = AnglePlot()
    qi = QuaternionInvestigator()
    source_selection = SourceSelection()

    qi.quaternion_rep_added.connect(source_selection.add_source)
    qi.angle.connect(angle_plot.update_data)

    layout.addWidget(source_selection.widget)
    layout.addWidget(angle_plot.widget)
    mw.show()

    qi.add_quaternion_rep(0)
    qi.add_quaternion_rep(1)

    mw2 = QtGui.QMainWindow()
    mw2.setCentralWidget(qi.widget)
    mw2.show()
    load_window_settings(mw, mw2)
    app.aboutToQuit.connect(partial(save_window_settings, mw, mw2))
    for w in [mw, mw2]:
        w.raise_()

    app.exec_()


if __name__ == '__main__':
    main()
