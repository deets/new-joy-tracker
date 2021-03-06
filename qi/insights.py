import bisect
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import PyQt5.QtWidgets as QtWidgets

from .common import angle_between_quats


class AnglePlot(pg.PlotWidget):

    PEN_COLOR = (255, 0, 0)

    def __init__(self, path):
        super().__init__(name='Angle Plot {}'.format(path[1:]))
        self._path = path
        self._curve = self.plot()
        self._curve.setPen(self.PEN_COLOR)
        self._data = []
        self._curve.setData(self._data)
        self._a, self._b = None, None
        self._quaternions = {}

    def update(self, path, sensor_no, quaternion):
        if path != self._path:
            return
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


class AccPlot(pg.PlotWidget):

    ACC_COLOR = (0, 255, 0)
    ACC_F_COLOR = (255, 255, 0)

    def __init__(self, path):
        super().__init__(name='Acc Plot {}'.format(path[1:]))
        self._path = path
        self._acc = self.plot()
        self._acc.setPen(self.ACC_COLOR)
        self._acc_data = []
        self._acc.setData(self._acc_data)

        self._acc_f = self.plot()
        self._acc_f.setPen(self.ACC_F_COLOR)
        self._acc_f_data = []
        self._acc_f.setData(self._acc_f_data)

        self._sensor_no = 0

    def update(self, path, sensor_no, acc, acc_f):
        if path != self._path:
            return
        self._acc_data.append(acc)
        self._acc.setData(self._acc_data)
        self._acc_f_data.append(acc_f)
        self._acc_f.setData(self._acc_f_data)

    def update_sensor_no(self, sensor_no):
        if sensor_no != self._sensor_no:
            self._sensor_no = sensor_no
            self._acc_data = []
            self._acc.setData(self._acc_data)
            self._acc_f_data = []
            self._acc_f.setData(self._acc_f_data)


class SourceSelection(QtCore.QAbstractListModel):

    indices = QtCore.pyqtSignal(int, int, name="indices")

    def __init__(self, path):
        super().__init__()
        self._path = path
        self._data = []

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

    def _add_source(self, source):
        self.beginInsertRows(
            QtCore.QModelIndex(),
            len(self._data), len(self._data)
        )
        self._data.append(source)
        self.endInsertRows()

    def update(self, path, sensor_no, _quat):
        if path == self._path and sensor_no not in self._data:
            self._add_source(sensor_no)


class SensorSelection(QtCore.QAbstractListModel):

    sensor_no = QtCore.pyqtSignal(int, name="sensor_no")

    def __init__(self, path):
        super().__init__()
        self._path = path
        self._data = []
        w = self.widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        w.setLayout(layout)

        self._sensor_no = QtWidgets.QComboBox()
        self._sensor_no.setModel(self)
        self._sensor_no.currentIndexChanged.connect(self.sensor_no)
        layout.addWidget(self._sensor_no)

    def data(self, index, role):
        if index.row() < len(self._data):
            return self._data[index.row()]
        return QtCore.QVariant()

    def rowCount(self, _parent):
        return len(self._data)

    def update(self, path, sensor_no, _acc, _acc_f):
        if path == self._path and sensor_no not in self._data:
            self.beginInsertRows(
                QtCore.QModelIndex(),
                len(self._data), len(self._data)
            )
            self._data.append(sensor_no)
            self.endInsertRows()


class ResetController(QtWidgets.QPushButton):

    reset = QtCore.pyqtSignal(str, name="reset")

    def __init__(self, path):
        super().__init__("Reset!")
        self._path = path
        self.clicked.connect(self.send_reset)

    def send_reset(self):
        self.reset.emit(self._path)


class MaskController(QtWidgets.QWidget):

    update_mask = QtCore.pyqtSignal(str, int, name="update_mask")

    def __init__(self, path):
        super().__init__()
        self._path = path
        self._checkboxes = {}
        self._state = {}
        self._layout = QtGui.QHBoxLayout()
        self.setLayout(self._layout)
        self._layout.addWidget(QtWidgets.QLabel(text="Mask:"))
        b = QtWidgets.QPushButton("Update")
        b.clicked.connect(self._update_mask)
        self._layout.addWidget(b)

    def _update_mask(self):
        mask = 0
        for sensor_no, is_masked in self._state.items():
            mask |= is_masked << sensor_no
        self.update_mask.emit(self._path, mask)

    def update(self, path, sensor_no, _quat):
        if path == self._path and sensor_no not in self._checkboxes:
            cb = self._checkboxes[sensor_no] = QtWidgets.QCheckBox(
                str(sensor_no), self
            )

            def update_state(state):
                self._state[sensor_no] = state == 2  # from the docs

            cb.stateChanged.connect(update_state)

            known = [(so, w) for so, w in self._checkboxes.items()]
            pos = bisect.bisect_left(known, (sensor_no, cb))
            pos += 1
            self._layout.insertWidget(pos, cb)


class GainController(QtWidgets.QWidget):

    update_gain = QtCore.pyqtSignal(str, int, float, name="update_gain")

    def __init__(self, path):
        super().__init__()
        self._path = path
        self._sensor_no = 0
        self._layout = QtGui.QHBoxLayout()
        self.setLayout(self._layout)
        b = QtWidgets.QPushButton("Update")
        b.clicked.connect(self._update_gain)

        s = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        s.setMinimum(0)
        s.setMaximum(100)
        s.setValue(100)
        self._gain = 100

        def gain_changed(v):
            self._gain = v

        s.valueChanged.connect(gain_changed)
        b.clicked.connect(self._update_gain)
        self._layout.addWidget(QtWidgets.QLabel(text="Gain:"))
        self._layout.addWidget(s)
        self._layout.addWidget(b)

    def _update_gain(self):
        self.update_gain.emit(self._path, self._sensor_no, self._gain / 100.0)

    def update_sensor_no(self, sensor_no):
        self._sensor_no = sensor_no


def setup_window_for_path(windowmanager, qi, path):
    # this is a slot that will be called all then
    # time so quickly do nothing if we don't have ot
    if path in windowmanager:
        return

    w = windowmanager.create_window(path)
    w.setWindowTitle(path)

    cw = QtGui.QWidget()
    w.setCentralWidget(cw)
    layout = QtGui.QVBoxLayout()
    cw.setLayout(layout)

    angle_plot = AnglePlot(path)
    source_selection = SourceSelection(path)
    mask_controller = MaskController(path)
    source_selection.indices.connect(angle_plot.update_indices)

    qi.quaternion.connect(source_selection.update)
    qi.quaternion.connect(angle_plot.update)
    qi.quaternion.connect(mask_controller.update)

    reset_button = ResetController(path)
    # qp = QuaternionProcessor()
    # qi.quaternion.connect(qp.update)
    reset_button.reset.connect(qi.reset)
    mask_controller.update_mask.connect(qi.update_mask)

    acc_plot = AccPlot(path)
    sensor_select = SensorSelection(path)
    gain_control = GainController(path)
    qi.acceleration.connect(sensor_select.update)
    qi.acceleration.connect(acc_plot.update)
    sensor_select.sensor_no.connect(acc_plot.update_sensor_no)
    sensor_select.sensor_no.connect(gain_control.update_sensor_no)
    gain_control.update_gain.connect(qi.update_gain)

    layout.addWidget(reset_button)
    layout.addWidget(mask_controller)
    layout.addWidget(source_selection.widget)
    layout.addWidget(angle_plot)
    layout.addWidget(sensor_select.widget)
    layout.addWidget(gain_control)
    layout.addWidget(acc_plot)

    w.show()
