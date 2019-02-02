from pyqtgraph.Qt import QtCore, QtGui


class WindowManager(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self._windows = []

    def save_window_settings(self):
        settings = QtCore.QSettings("deets_design", "quaternion-investigator")
        for window in self._windows:
            name = window.objectName()
            settings.setValue(
                "geometry-{}".format(name),
                window.saveGeometry()
            )
            settings.setValue(
                "windowState-{}".format(name),
                window.saveState(),
            )

    def load_window_settings(self):
        settings = QtCore.QSettings("deets_design", "quaternion-investigator")
        for window in self._windows:
            name = window.objectName()
            saved_geometry = settings.value("geometry-{}".format(name))
            if saved_geometry is not None:
                window.restoreGeometry(saved_geometry)
            saved_state = settings.value("windowState-{}".format(name))
            if saved_state is not None:
                window.restoreState(saved_state)

    def __iadd__(self, window):
        self._windows.append(window)
        return self
