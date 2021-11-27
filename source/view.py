import os
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import pyqtSignal


class SeekableSlider(QSlider):

    onClicked = pyqtSignal()
    onReleased = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if os.name == "nt":
            self.onClicked.emit()
            perc = round(event.x() / self.width(), 5)
            value = int(perc * self.maximum())
            self.setValue(value)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if os.name == "nt":
            perc = round(event.x() / self.width(), 5)
            self.onReleased.emit(perc)


def set_button_icon(btn, icon_path):
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    btn.setIcon(icon)


def set_label_image(label, icon_path):
    pixmap = QPixmap(icon_path)
    label.setPixmap(pixmap)
    label.setScaledContents(True)
    label.show()
