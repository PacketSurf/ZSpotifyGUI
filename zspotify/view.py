from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QImage, QPixmap

def set_button_icon(btn, icon_path):
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    btn.setIcon(icon)

def set_label_image(label, icon_path):
    pixmap = QPixmap(icon_path)
    label.setPixmap(pixmap)
    label.setScaledContents(True)
    label.show()
