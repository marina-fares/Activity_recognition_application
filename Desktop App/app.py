from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QLineEdit,QFileDialog,QMainWindow,QApplication, QFileSystemModel
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSlot
import icons_rc
import traceback, sys
import os
import vlc

from os.path import expanduser
import moviepy
import moviepy.editor

from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QTreeView, QGridLayout

from kinetics_i3d_master.preprocessing import preprocessing
from kinetics_i3d_master.evaluate_sample import activity_recogniton


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main2.ui', self)
        self.show()
        
        self.start_video()
        self.handel_buttons()
        self.handel_style()

        self.file_name = None
        self.output_path = None
        self.first_run = True
        self.working_dir = os.getcwd()
        self.main_output_folder_structure = None

        self.history_layout = QGridLayout()
        self.tab_3.setLayout(self.history_layout)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar_label = QLabel("Program Ready !!",self)
        self.statusBar_label.setStyleSheet("color: black")
        self.statusBar.addWidget(self.statusBar_label)
        self.statusBar.show()
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())


    def handel_style(self):
        self.progressBar.setVisible(False)
        self.progressBar.setValue(0)
        self.tabWidget.setCurrentIndex(0)
        self.home_btn.setStyleSheet("background-color : #a8dadc; border:0px; margin:0px")
        self.output_btn.setStyleSheet("QPushButton { background-color: #1d3557; border:1px solid black; border-radius:5px; color:black; }"
                                    "QPushButton:pressed { background-color: #a8dadc }" )
        self.browse_btn.setStyleSheet("QPushButton { background-color: #1d3557; border:1px solid black; border-radius:5px; color:black; }"
            "QPushButton:pressed { background-color: #a8dadc }" )
        self.start_btn.setStyleSheet("QPushButton { background-color: #1d3557; border:1px solid black; border-radius:5px; color:black; }"
            "QPushButton:pressed { background-color: #a8dadc }" )
        self.play_btn.setStyleSheet("QPushButton { background-color: #1d3557; border:1px solid black; border-radius:5px; color:black; }"
            "QPushButton:pressed { background-color: #a8dadc }" )


    def draw(self, main_folder_path):        
        if self.first_run :
            dirpath = main_folder_path
            self.model = QFileSystemModel()
            self.model.setRootPath(dirpath)
            self.tree =  QTreeView()
            self.tree.setModel(self.model)
            self.tree.setRootIndex(self.model.index(dirpath))
            self.gridLayout_5.addWidget(self.tree)
            self.frame_2.setLayout(self.gridLayout_5)
            self.first_run = False
            self.tree.doubleClicked.connect(self.runvideo)
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
        if sys.platform.startswith('linux'):	
            self.mediaPlayer = QmediaPlayer(None, QmediaPlayer.VideoSurface)
        elif sys.platform == "win32":
            self.instance = vlc.Instance()
            self.mediaPlayer = self.instance.media_player_new()
        self.videoWidget = QVideoWidget()
        self.videoWidget.setStyleSheet("background-color : black")
        self.videoWidget.setFixedHeight(300)
        self.play_btn = QPushButton()
        self.play_btn.setEnabled(False)
        self.play_btn.setFixedHeight(30)
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.setText("Play")
        self.play_btn.setStyleSheet("color : white")
        self.play_btn.clicked.connect(self.play)
        self.h_slider = QSlider(Qt.Horizontal)
        self.h_slider.setMaximum(1000)
        self.h_slider.sliderMoved.connect(self.setPosition)
        if sys.platform.startswith('linux'):
            self.mediaPlayer.setVideoOutput(self.videoWidget)
            #self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
            self.mediaPlayer.positionChanged.connect(self.positionChanged)
            self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.gridLayout_5.addWidget(self.videoWidget)
        self.gridLayout_5.addWidget(self.h_slider)
        self.gridLayout_5.addWidget(self.play_btn)
        self.frame_2.setLayout(self.gridLayout_5)
        self.isPaused = False
        if sys.platform == "win32":
            self.timer = QTimer(self)
            self.timer.setInterval(200)
            self.timer.timeout.connect(self.update_position_slider)
        
        
    def abrir(self,path):
        # create the media
        if sys.platform.startswith('linux'):	
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        elif sys.platform == "win32":
            if sys.version < '3':
                path = unicode(path)
            self.media = self.instance.media_new(path)
            self.mediaPlayer.set_media(self.media)
            self.media.parse()
            self.play_btn.setEnabled(True)
            self.mediaPlayer.set_hwnd(self.videoWidget.winId())
        self.play()


    def play(self):
        if sys.platform.startswith('linux'):
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                self.mediaPlayer.pause()
                self.play_btn.setText("Play")
            else:
                self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                self.mediaPlayer.play()
                self.play_btn.setText("Pause")
        elif sys.platform == "win32":
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
        self.h_slider.setValue(self.mediaPlayer.get_position() * 1000)
        if not self.mediaPlayer.is_playing():
            self.timer.stop()
            if not self.isPaused:
                self.Stop()
    
    def Stop(self):
        self.h_slider.setValue(0)
        self.mediaPlayer.stop()
        self.play_btn.setText("Play")
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.setEnabled(False)

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
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.play_btn.setText("Pause")
        else:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.play_btn.setText("Play")
        

    def handel_buttons(self):
        self.start_btn.clicked.connect(self.start_processing)
        self.browse_btn.clicked.connect(self.browse_video)
        self.output_btn.clicked.connect(self.output_path_)
        self.home_btn.clicked.connect(self.homefun)
        self.video_btn.clicked.connect(self.videofun)
        self.history_btn.clicked.connect(self.historyfun)
        

    def homefun(self):
        self.home_btn.setStyleSheet("background-color : #a8dadc")
        self.video_btn.setStyleSheet("background-color : #1d3557")
        self.history_btn.setStyleSheet("background-color : #1d3557")
        self.tabWidget.setTabEnabled(0,True)
        self.tabWidget.setCurrentIndex(0)

    def videofun(self):
        self.video_btn.setStyleSheet("background-color : #a8dadc")
        self.home_btn.setStyleSheet("background-color : #1d3557")
        self.history_btn.setStyleSheet("background-color : #1d3557")
        self.tabWidget.setTabEnabled(1,True)
        self.tabWidget.setCurrentIndex(1)

    def historyfun(self):
        self.history_btn.setStyleSheet("background-color : #a8dadc")
        self.home_btn.setStyleSheet("background-color : #1d3557")
        self.video_btn.setStyleSheet("background-color : #1d3557")
        self.tabWidget.setTabEnabled(2,True)
        self.tabWidget.setCurrentIndex(2)


    def start_processing(self):
        if(self.file_name):
            os.chdir(self.working_dir)
            numpy_frames = preprocessing(self.file_name)
            self.progressBar.setVisible(True)
            self.show_status("Starting Model !!")
            if not self.output_path:
                self.output_path = os.path.dirname(os.path.abspath(self.file_name))
            worker = Worker(activity_recogniton,self.file_name,numpy_frames,self.output_path) 
            worker.signals.result.connect(self.draw_folder_tree)
            worker.signals.finished.connect(self.thread_complete)
            worker.signals.progress.connect(self.progress_fn)
            worker.signals.status.connect(self.show_status)
            self.threadpool.start(worker) 


    def show_status(self,status):
        self.statusBar_label.setText(status)

    def thread_complete(self):
        self.statusBar_label.setText("Model Finished Processing Input Video !!")

    def progress_fn(self,progress_value):
        self.progressBar.setValue(progress_value)    

    def draw_folder_tree(self,path):
        self.draw(path)
        self.draw_history(path)
        self.tabWidget.setTabEnabled(1,True)
        self.tabWidget.setCurrentIndex(1)
        self.video_btn.setStyleSheet("background-color : #a8dadc")
        self.home_btn.setStyleSheet("background-color : #1d3557")
        self.progressBar.setVisible(False)
        self.progressBar.setValue(0)
    
            
    def output_path_(self):
        fileName = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if fileName:
            self.output_line.setText(fileName)
            self.output_path = fileName
        

    def browse_video(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"Input Video", "","Videos (*.mp4 *.avi)", options=options)
        if fileName:
            self.input_line.setText(fileName)
            self.file_name = fileName


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    status = pyqtSignal(object)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()    

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress
        self.kwargs['status_callback'] = self.signals.status 
    

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  
        finally:
            self.signals.finished.emit()

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui()
    app.exec_()



