import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import PyQt5.QtWidgets as QtWidgets

from .common import angle_between_quats


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


def setup_window_for_path(windowmanager, path):
    # this is a slot that will be called all then
    # time so quickly do nothing if we don't have to
    if path in windowmanager:
        return

    w = windowmanager.create_window(path)
    w.setWindowTitle(path)
    w.show()
