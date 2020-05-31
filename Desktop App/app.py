from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QLineEdit,QFileDialog,QMainWindow,QApplication, QFileSystemModel
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSlot
import icons_rc
import sys
import os
import vlc

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
            self.tree.doubleClicked.connect(self.runvideo)
            self.first_run = False
        else :
            dirpath = main_folder_path            
            self.model.setRootPath(dirpath)
            self.tree.setModel(self.model)
            self.tree.setRootIndex(self.model.index(dirpath))
            self.tree.doubleClicked.connect(self.runvideo)

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


    def start_video(self):	
        #self.mediaPlayer = QmediaPlayer(None, QmediaPlayer.VideoSurface)
        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaPlayer = self.instance.media_player_new()
        self.videoWidget = QVideoWidget()
        self.videoWidget.setFixedHeight(250)
        self.videoWidget.setFixedWidth(500)
        self.play_btn.setEnabled(False)
        self.play_btn.setFixedHeight(24)
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.clicked.connect(self.play)
        #self.h_slider.setRange(0, 1000)
        self.h_slider.setMaximum(1000)
        self.h_slider.sliderMoved.connect(self.setPosition)
        #self.mediaPlayer.setVideoOutput(videoWidget)
        #self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        #self.mediaPlayer.positionChanged.connect(self.positionChanged)
        #self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.verticalLayout.addWidget(self.videoWidget,1)
        self.frame_2.setLayout(self.verticalLayout)
        self.isPaused = False
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_position_slider)
        
        
        
		
    def abrir(self,path):
         # create the media
        if sys.version < '3':
            path = unicode(path)
        self.media = self.instance.media_new(path)
        # put the media in the media player
        self.mediaPlayer.set_media(self.media)
        # parse the metadata of the file
        self.media.parse()
        #self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.play_btn.setEnabled(True)
        if sys.platform.startswith('linux'): # for Linux using the X Server
            self.mediaPlayer.set_xwindow(self.videoWidget.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaPlayer.set_hwnd(self.videoWidget.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaPlayer.set_nsobject(int(self.videoWidget.winId()))
        self.play()

    def play(self):
        if self.mediaPlayer.is_playing():
            self.mediaPlayer.pause()
            self.play_btn.setText("Play")
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.isPaused = True
        else:
            self.mediaPlayer.play()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.play_btn.setText("Pause")
            self.timer.start()
            self.isPaused = False

    def update_position_slider(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.h_slider.setValue(self.mediaPlayer.get_position() * 1000)

        if not self.mediaPlayer.is_playing():
            # no need to call this function if nothing is played
            self.timer.stop()
            if not self.isPaused:
                # after the video finished, the play button stills shows
                # "Pause", not the desired behavior of a media player
                # this will fix it
                self.Stop()
    
    def Stop(self):
        """Stop player
        """
        self.mediaPlayer.stop()
        self.play_btn.setText("Play")

        
    def positionChanged(self, position):
        self.h_slider.setValue(position)

    def durationChanged(self, duration):
	    self.h_slider.setRange(0, duration)

    def setPosition(self, position):
	    self.mediaPlayer.set_position(position / 1000.0)

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
        #if(self.file_name):
        os.chdir(self.working_dir)
            #numpy_frames = preprocessing(self.file_name)
            #if not self.output_path:
            #    self.output_path = os.path.dirname(os.path.abspath(self.file_name))
            #self.main_output_folder_structure = activity_recogniton(self.file_name,numpy_frames,self.output_path,self.first_run)
            
        self.draw( "D:/WorkSpace/GP/GP_design/Desktop App/kinetics_i3d_master/data")
        self.draw_history( "D:/WorkSpace/GP/GP_design/Desktop App/kinetics_i3d_master/data")
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
