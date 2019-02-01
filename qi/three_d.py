from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl


class QuaternionRep(QtCore.QObject):
    SIZE = QtGui.QVector3D(3, 3, 3)
    # z is green
    # y is yellow
    # x is blue

    def __init__(self, w, key):
        super().__init__()
        self._cylinder = gl.GLAxisItem(size=self.SIZE)
        w.addItem(self._cylinder)
        self._key = key
        self.update(QtGui.QQuaternion())

    def update(self, quat):
        c = self._cylinder
        c.resetTransform()
        c.transform().translate(self._key * 5, 0, 1)
        c.transform().rotate(quat)
