from pyqtgraph.Qt import QtCore, QtGui


class WindowManager(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self._windows = {}
        self._settings = QtCore.QSettings("deets_design", "quaternion-investigator")

    def save_window_settings(self):
        for name, window in self._windows.items():
            self._settings.setValue(
                "geometry-{}".format(name),
                window.saveGeometry()
            )
            self._settings.setValue(
                "windowState-{}".format(name),
                window.saveState(),
            )

    def load_window_settings(self):
        for name, window in self._windows.items():
            self._load_window_settings(name, window)

    def _load_window_settings(self, name, window):
        saved_geometry = self._settings.value("geometry-{}".format(name))
        if saved_geometry is not None:
            window.restoreGeometry(saved_geometry)
        saved_state = self._settings.value("windowState-{}".format(name))
        if saved_state is not None:
            window.restoreState(saved_state)

    def __iadd__(self, window):
        name = window.objectName()
        assert(name not in self)
        self._windows[name] = window
        return self

    def __getitem__(self, name):
        return self._windows[name]

    def __contains__(self, name):
        return name in self._windows

    def create_window(self, name):
        assert name not in self
        w = QtGui.QMainWindow()
        w.setObjectName(name)
        self += w
        self._load_window_settings(name, w)
        return w
