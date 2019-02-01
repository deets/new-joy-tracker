import math
from pyqtgraph.Qt import QtGui, QtCore


def debug_trace():
  from pdb import set_trace
  QtCore.pyqtRemoveInputHook()
  set_trace()


def angle_between_quats(qa, qb):
    vec = QtGui.QVector3D(1, 0, 0)
    va = qa.rotatedVector(vec)
    vb = qb.rotatedVector(vec)
    vector_cos = va.dotProduct(va, vb)
    try:
        return math.acos(vector_cos) / math.pi * 180
    except ValueError:
        debug_trace()
