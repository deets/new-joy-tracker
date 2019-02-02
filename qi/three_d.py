import pathlib
import PIL.Image as Image
import PIL.ImageFont as ImageFont
import PIL.ImageDraw as ImageDraw
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl


SQUARE_DEAL = pathlib.Path(__file__).parent / "square-deal.ttf"
assert SQUARE_DEAL.exists()


class QuaternionRep(QtCore.QObject):
    SIZE = QtGui.QVector3D(3, 3, 3)
    # z is green
    # y is yellow
    # x is blue

    def __init__(self, w, path, sensor_no):
        super().__init__()
        a = self._anchor = gl.GLGraphicsItem.GLGraphicsItem()
        self._gizmo = gl.GLAxisItem(size=self.SIZE)
        self._gizmo.setParentItem(a)
        name = "{} {}".format(path[1:], sensor_no)
        sd_font = ImageFont.truetype(str(SQUARE_DEAL), 20)

        temp_image = Image.new('RGBA', (2, 2), (0, 0, 0, 0))
        width, height = ImageDraw.Draw(temp_image).textsize(name, sd_font)
        txt_image = Image.new('RGBA', (width + 2, height + 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_image)
        draw.text((1, 1), name, font=sd_font, fill=(255, 255, 255, 128))
        tex1 = np.asarray(txt_image)
        v1 = gl.GLImageItem(tex1)
        v1.setParentItem(a)
        v1.scale(0.05, 0.05, 0.05)
        w.addItem(a)
        w.addItem(v1)
        w.addItem(self._gizmo)
        self._sensor_no = sensor_no
        self.update(QtGui.QQuaternion())

    def update(self, quat):
        c = self._anchor
        c.resetTransform()
        c.transform().translate(self._sensor_no * 5, 0, 1)
        c.transform().rotate(quat)
