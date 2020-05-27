from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QLineEdit,QFileDialog,QMainWindow,QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSlot
import icons_rc
import sys
import os

from kinetics_i3d_master.preprocessing import preprocessing
from kinetics_i3d_master.evaluate_sample import activity_recogniton

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('design3.ui', self)
        self.show()
        self.handel_buttons()
        self.file_name = None
        self.output_path = None
        self.first_run = True
        self.working_dir = os.getcwd()
        self.main_output_folder_structure = None
        

    def handel_buttons(self):
        self.start_btn.clicked.connect(self.start_processing)
        self.browse_btn.clicked.connect(self.browse_video)

    def start_processing(self):
        print("Done")
        print(self.comboBox.currentText())
        if(self.file_name):
            os.chdir(self.working_dir)
            numpy_frames = preprocessing(self.file_name)
            if not self.output_path:
                self.output_path = os.path.dirname(os.path.abspath(self.file_name))
            self.main_output_folder_structure = activity_recogniton(self.file_name,numpy_frames,self.output_path,self.first_run)
            self.first_run = False
            
            

    def browse_video(self):
        print("Done")
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Input Video", "","Videos (*.mp4 *.avi)", options=options)
        if fileName:
            print(fileName)
            self.file_name = fileName
            #print(os.path.dirname(os.path.abspath(fileName)))
            #print(os.getcwd())
            #os.chdir(os.path.dirname(os.path.abspath(fileName)))
            #print(os.getcwd())
            #dir_name = "test"
            #os.mkdir(dir_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui()
    app.exec_()


''' 
buttons' names ::
1. browse_btn
2. start_btn
3. home_btn
4. video_btn
5. history_btn
'''