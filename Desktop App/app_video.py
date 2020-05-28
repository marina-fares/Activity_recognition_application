from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QLineEdit,QFileDialog,QMainWindow,QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSlot
import icons_rc
import sys

from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

from PyQt5.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar



class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('design_video.ui', self)
        self.start_video()
        self.show()
        self.file_name = None


    def start_video(self):
		
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()
        videoWidget.setFixedHeight(250)
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
        self.abrir()
		
    def abrir(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile("test_video.mp4")))
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


    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.play_btn.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_btn.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))
    

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
