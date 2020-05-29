from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QLineEdit,QFileDialog,QMainWindow,QApplication, QFileSystemModel
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSlot
import icons_rc
import sys
import os

from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

from kinetics_i3d_master.preprocessing import preprocessing
from kinetics_i3d_master.evaluate_sample import activity_recogniton

from PyQt5.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QTreeView, QGridLayout

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main2.ui', self)
        self.show()
        self.start_video()
        self.handel_buttons()
        self.file_name = None
        self.output_path = None
        self.first_run = True
        self.working_dir = os.getcwd()
        self.main_output_folder_structure = None

        self.history_layout = QGridLayout()
        self.tab_3.setLayout(self.history_layout)

        self.tabWidget.setTabEnabled(1,False)
        self.tabWidget.setTabEnabled(2,False)
        self.tabWidget.setCurrentIndex(0)

    def draw(self, main_folder_path):        
        if self.first_run :
            dirpath = main_folder_path
            self.model = QFileSystemModel()
            self.model.setRootPath(dirpath)
            self.tree =  QTreeView()
            self.tree.setModel(self.model)
            self.tree.setRootIndex(self.model.index(dirpath))
            self.verticalLayout.addWidget(self.tree)
            self.frame_2.setLayout(self.verticalLayout)
            self.tree.doubleClicked.connect(self.test)
            self.first_run = False
        else :
            dirpath = main_folder_path            
            self.model.setRootPath(dirpath)
            self.tree.setModel(self.model)
            self.tree.setRootIndex(self.model.index(dirpath))
            self.tree.doubleClicked.connect(self.test)

    def draw_history(self, main_folder_path):        
        dirpath = main_folder_path
        self.model_h = QFileSystemModel()
        self.model_h.setRootPath(dirpath)
        self.tree_2 =  QTreeView()
        self.tree_2.setModel(self.model_h)
        self.tree_2.setRootIndex(self.model_h.index(dirpath))

        self.history_layout.addWidget(self.tree_2)
        self.tree.doubleClicked.connect(self.runvideo)
        self.first_run = False

    def runvideo(self, signal):
        file_path=self.model_h.filePath(signal)
        self.abrir(file_path)


    def test(self, signal):
        file_path=self.model.filePath(signal)
        self.abrir(file_path)

    
        

    def start_video(self):	
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()
        videoWidget.setFixedHeight(250)
        videoWidget.setFixedWidth(500)
        self.play_btn.setEnabled(False)
        self.play_btn.setFixedHeight(24)
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.clicked.connect(self.play)
        self.h_slider.setRange(0, 0)
        self.h_slider.sliderMoved.connect(self.setPosition)
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

        self.verticalLayout.addWidget(videoWidget,1)
        self.frame_2.setLayout(self.verticalLayout)
        #self.abrir("/home/marina/Graduation project/kinetics-marina/GP_design/Desktop App/test_video.mp4")
		
    def abrir(self,path):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.play_btn.setEnabled(True)
        self.play()

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

        
    def positionChanged(self, position):
        self.h_slider.setValue(position)

    def durationChanged(self, duration):
	    self.h_slider.setRange(0, duration)

    def setPosition(self, position):
	    self.mediaPlayer.setPosition(position)

    def handleError(self):
	    self.play_btn.setEnabled(False)
	    self.statusbar.showMessage("Error: " + self.mediaPlayer.errorString())

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.play_btn.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_btn.setIcon(
            self.style().standardIcon(QStyle.SP_MediaPlay))
        

    def handel_buttons(self):
        self.start_btn.clicked.connect(self.start_processing)
        self.browse_btn.clicked.connect(self.browse_video)
        self.home_btn.clicked.connect(self.homefun)
        self.video_btn.clicked.connect(self.videofun)
        self.history_btn.clicked.connect(self.historyfun)
        

    def homefun(self):
        self.tabWidget.setCurrentIndex(0)

    def videofun(self):
        self.tabWidget.setCurrentIndex(1)

    def historyfun(self):
        self.tabWidget.setCurrentIndex(2)


    def start_processing(self):
        print(self.comboBox.currentText())
        if(self.file_name):
            os.chdir(self.working_dir)
            numpy_frames = preprocessing(self.file_name)
            if not self.output_path:
                self.output_path = os.path.dirname(os.path.abspath(self.file_name))
            self.main_output_folder_structure = activity_recogniton(self.file_name,numpy_frames,self.output_path,self.first_run)
            
            self.draw( self.main_output_folder_structure.path)
            self.draw_history( self.main_output_folder_structure.path)
            self.tabWidget.setCurrentIndex(1)
            
            

    def browse_video(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Input Video", "","Videos (*.mp4 *.avi)", options=options)
        if fileName:
            self.input_line.setText(fileName)
            #print(fileName)
            self.file_name = fileName
        else:
            self.file_name = self.input_line.text()

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
