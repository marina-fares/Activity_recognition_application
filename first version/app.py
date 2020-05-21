from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSlot
import icon_rc

import sys

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('design3.ui', self)
        self.show()
        self.handel_buttons()

    def handel_buttons(self):
        button = self.start_btn.clicked.connect(self.test)

    def test(self):
        print("Done")



app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()