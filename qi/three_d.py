from pyqtgraph.Qt import QtCore
import pyqtgraph.opengl as gl
import numpy as np


class QuaternionRep(QtCore.QObject):
    LENGTH = 3

    def __init__(self, w):
        super().__init__()

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

    def update(self, quat):
        c = self._cylinder
        c.resetTransform()
        c.transform().rotate(quat)
        c.transform().translate(0, 0, -self.LENGTH / 2)
