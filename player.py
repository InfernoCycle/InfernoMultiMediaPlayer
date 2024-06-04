from PySide6.QtWidgets import QMessageBox, QFileDialog, QStatusBar, QMenu, QMainWindow, QComboBox, QTabWidget, QAbstractItemView, QListWidgetItem, QListWidget, QSizePolicy, QLineEdit, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QShortcut, QKeySequence
from widget import Center
from mBar import MenuBar
import math
import pyscreenshot as ImageGrab
import time
import random
import sys
import os

import asyncio

class MPlayer(QMainWindow):
  def __init__(self):
    super().__init__()
    self.loaded = False
    self.menu_bar = MenuBar()
    self.setWindowTitle("Inferno Player")
    self.setMinimumSize(600, 400)
    
    QShortcut(QKeySequence(Qt.Key_S), self, self.screenshot)
    
    menu = self.menuBar()
    
    file = menu.addMenu("File")
    open_action = file.addAction("Open")
    #close_action = file.addAction("Close")
    
    open_action.triggered.connect(self.open_file)
    
    about = menu.addMenu("About")
    version_action = about.addAction("Version")
    version_action.triggered.connect(self.show_version)
    about_action = about.addAction("Source")
    about_action.triggered.connect(self.show_git_repo)
    owner_action = about.addAction("Owner")
    owner_action.triggered.connect(self.show_owner)
    
    option_action = menu.addMenu("Options")
    video_screenshot = option_action.addAction("Screenshot")
    video_screenshot.triggered.connect(self.screenshot)
    show_keys = option_action.addAction("Shortcuts")
    show_keys.triggered.connect(self.show_shortcuts)
    
    self.MainWidget = Center()
    #self.setStatusBar(self.MainWidget.status_bar)
    self.setCentralWidget(self.MainWidget)

    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    path_to_style = os.path.abspath(os.path.join(bundle_dir,'style.css'))

    with open(path_to_style, "r") as style:
      self.setStyleSheet(style.read())
  
  def open_file(self):
    filename = QFileDialog(self).getOpenFileName(filter="Text files (*.mp3 *.mp4)")
    if(filename[0] == ''):
      return
    else:
      self.loaded = False

      self.MainWidget.player.mediaStatusChanged.connect(self.notify)
      self.MainWidget.player.errorOccurred.connect(self.err)

      self.MainWidget.video_seek.setSliderPosition(0)
      
      #print(self.MainWidget.player.mediaStatus().name)
      #print(self.MainWidget.player.playbackState())
      
      self.MainWidget.stop_play()
      time.sleep(1) #gives time for program to debuffer loaded media
      self.MainWidget.player.setSource(QUrl())  
      self.MainWidget.player.setSource(QUrl(filename[0]))

      self.MainWidget.player.durationChanged.connect(self.dur_changed)
  
  def close_file(self):
    pass
  
  def show_version(self):
    self.menu_bar.version_msg.information(self,"Version", "Version 1.0", QMessageBox.Ok)
    
  def show_git_repo(self):
    self.menu_bar.source_msg.information(self,"Source", "No Sources Available", QMessageBox.Ok)
  
  def show_shortcuts(self):
    self.menu_bar.show_keys()
  
  def screenshot(self):
    if(self.MainWidget.player.source().fileName() != ''):
      if(self.MainWidget.player.hasVideo()):
        #print(self.MainWidget.videoWidget.contentsRect())
        vidWidget_w = self.MainWidget.videoWidget.contentsRect().width()
        vidWidget_h = self.MainWidget.videoWidget.contentsRect().height()
        winWidget_w = self.contentsRect().width()
        winWidget_h = self.contentsRect().height()
        
        window_x1_cord = self.geometry().topLeft().x()
        window_y1_cord = self.geometry().topLeft().y()
        window_x2_cord = self.geometry().bottomRight().x()
        window_y2_cord = self.geometry().bottomRight().y()
        
        vid_x1_cord = self.MainWidget.videoWidget.geometry().topLeft().x()
        vid_y1_cord = self.MainWidget.videoWidget.geometry().topLeft().y()
        vid_x2_cord = self.MainWidget.videoWidget.geometry().bottomRight().x()
        vid_y2_cord = self.MainWidget.videoWidget.geometry().bottomRight().y()
        
        """
        print(vid_x1_cord)
        print(vid_y1_cord)
        print(vid_x2_cord)
        print(vid_y2_cord)
        
        print()
        
        print(window_x1_cord)
        print(window_y1_cord)
        print(window_x2_cord)
        print(window_y2_cord)
        """
        
        #pulls the screenshot down starting from the menubar (0 means menubar is shown fully)
        menubar_added = 22
        
        #print(self.geometry())
        
        im=ImageGrab.grab(childprocess=False,bbox=(window_x1_cord+vid_x1_cord, window_y1_cord+vid_y1_cord+menubar_added, window_x2_cord-vid_x1_cord, window_y2_cord-(winWidget_h-vidWidget_h)+menubar_added+vid_y1_cord))
        #im.show()
        t = time.time()
        local = time.localtime(t)
        
        saved_file = f"Screenshot_{random.randint(1000,9999)}_{local.tm_mon}-{local.tm_mday}-{local.tm_year}_{local.tm_hour}-{local.tm_min}-{local.tm_sec}.jpg"

        im.save(f"./{saved_file}")
        
        #self.menu_bar.show_screenshot_msg(saved_file)
  
  def notify(self, status):
    if(status.name == "LoadingMedia"):
      self.loaded = False
    
    if(not self.loaded):
      if(status.name == "LoadedMedia"):
        self.loaded = True
    #print(status)
  
  def err(self, error, errorStr):
    pass
    #print(error)
    #print(errorStr)

  def dur_changed(self):
    duration = self.MainWidget.player.duration()
    max_length = str(round(duration/1000/60, 2))
    
    max_length_str = ""
    
    minutes = (duration/(1000 * 60)) % 60
    seconds = (duration/1000) % 60
    hours = (duration/(1000 * 60 * 60)) % 24
    
    if(len(str(math.floor(seconds)))>1):
      self.MainWidget.max_pos.setText(str(minutes)[0]+":"+str(math.floor(seconds)))
    else:
      self.MainWidget.max_pos.setText(str(minutes)[0]+":0"+str(math.floor(seconds)))

    self.MainWidget.video_seek.setMaximum(duration)
    #self.MainWidget.max_pos.setText(max_length_str)
    self.MainWidget.video_loaded = True
    
  def show_owner(self):
    self.menu_bar.show_true_owner()
  
  #extra function if needed
  def load_up(self, filename):
    pass
