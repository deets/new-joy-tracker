#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3.7
# -*- mode: python -*-
import sys
for p in [
        "/usr/local/Cellar/pyqt5/5.10.1_1/lib/python3.7/site-packages",
        "/usr/local/Cellar/sip/4.19.8_6/lib/python3.7/site-packages",
        ]:
    sys.path.append(p)



from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np


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

    def __init__(self):
        super().__init__()
        self._rot = 0.0

        self._w = w = gl.GLViewWidget()
        w.show()
        w.setWindowTitle('pyqtgraph example: GLMeshItem')
        w.setCameraPosition(distance=40)

        g = gl.GLGridItem()
        g.scale(2, 2, 1)
        w.addItem(g)

        self._quaternion_reps = {}

        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._update)
        self._timer.start(10)

    def _update(self):
        self._rot += 1  # degrees
        for qrep in self._quaternion_reps.values():
            qrep.rotate(self._rot)

    def add_quaternion_rep(self, key):
        self._quaternion_reps[key] = QuaternionRep(self._w)


def main():
    app = QtGui.QApplication([])
    qi = QuaternionInvestigator()
    qi.add_quaternion_rep(0)
    app.exec_()


if __name__ == '__main__':
    main()
