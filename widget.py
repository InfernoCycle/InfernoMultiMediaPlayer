from PySide6.QtWidgets import QStatusBar, QSizePolicy, QSlider, QLineEdit, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtGui import QIcon, QKeySequence, QAction, QKeyEvent, QShortcut
from PySide6.QtCore import Qt, QEvent
import math
import sys
import os

class Center(QWidget):
  def __init__(self):
    super().__init__()
    self.isBundle = False
    #get path from temporary folder
    self.bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    
    if(self.isBundle):
      self.bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    else:
      self.bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__))+"/icons")
      
    #keyboard_events
    self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    #save PC resources committee
    self.seeking_started = False
    
    self.default_volume = 20
    self.auto_seek = 5
    
    self.status_bar = QStatusBar()
    self.status_bar.setStyleSheet("background-color:darkgray;")
    self.status_timeout = 350
    self.play_icon = QIcon(os.path.abspath(os.path.join(self.bundle_dir,"16px-Octicons-playback-play.svg.png"))).setThemeName("play")
    self.pause_icon = QIcon(os.path.abspath(os.path.join(self.bundle_dir,"Octicons-playback-pause.svg.png"))).setThemeName("pause")
    
    layout = QVBoxLayout()
    self.player = QMediaPlayer(self)
    self.videoWidget = QVideoWidget(self)
    
    #credit for figuring out shortcut keys:
    #https://stackoverflow.com/questions/60442806/qvideowidget-in-full-screen-mode-no-longer-responds-to-hotkeys-or-mouse-wheel
    
    #for available keys visit: https://www.klayout.de/doc/code/class_Qt::Key.html
    QShortcut(QKeySequence(Qt.Key_F), self.videoWidget, self.toggle_fullscreen)
    QShortcut(QKeySequence(Qt.Key_Escape), self.videoWidget, self.escape_fullscreen)
    QShortcut(QKeySequence(Qt.Key_Right), self.videoWidget, self.play_fast_f)
    QShortcut(QKeySequence(Qt.Key_Left), self.videoWidget, self.play_rewind)
    QShortcut(QKeySequence(Qt.Key_Up), self.videoWidget, self.volume_key_up)
    QShortcut(QKeySequence(Qt.Key_Down), self.videoWidget, self.volume_key_down)
    QShortcut(QKeySequence(Qt.Key_Space), self.videoWidget, self.space_play)
    
    audioDevice = QMediaDevices()
    self.audioOuput = QAudioOutput(audioDevice.defaultAudioOutput(), self)
    self.player.setAudioOutput(self.audioOuput)
    self.audioOuput.setVolume(self.default_volume/100)
    self.player.setVideoOutput(self.videoWidget)
    self.player.positionChanged.connect(self.playing)
    
    #player inserted into layout
    layout.addWidget(self.videoWidget)
    
    #seeker_slider include number and fullscreen button
    seeker_layout = QHBoxLayout()
    self.video_seek = QSlider(Qt.Horizontal, self)
    self.video_seek.setObjectName("video_line")
    self.video_seek.setMinimum(0)
    self.video_seek.sliderMoved.connect(self.video_move)
    self.video_seek.sliderReleased.connect(self.seek_release)
    
    self.current_pos = QLabel("0:00", self)
    self.max_pos = QLabel("0:00", self)
    self.current_pos.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    self.max_pos.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    
    self.fullscreen = QPushButton("", self)
    self.fullscreen.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    self.fullscreen.setIcon(QIcon(os.path.abspath(os.path.join(self.bundle_dir,"maximize-solid.png"))))
    self.fullscreen.setObjectName("full_scr")
    self.fullscreen.setToolTip("Fullscreen")
    self.fullscreen.clicked.connect(self.go_fullscreen)
    
    #video seeker inserted into layout
    seeker_layout.addWidget(self.current_pos)
    seeker_layout.addWidget(self.video_seek)
    seeker_layout.addWidget(self.max_pos)
    seeker_layout.addWidget(self.fullscreen)
    layout.addLayout(seeker_layout)
    
    ##Controls options
    controls = QHBoxLayout()
    #volume control
    volume_layout = QGridLayout()
    
    self.low_label = QLabel(str(self.default_volume)+"%", self)
    self.low_label.setMaximumWidth(30)
    self.low_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    high_label = QLabel("100", self)
    high_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    self.volume = QSlider(Qt.Horizontal, self)
    self.volume.setMinimum(0)
    self.volume.setMaximum(100)
    self.volume.setProperty("volume_slider", True)
    self.volume.setSliderPosition(self.default_volume)
    self.volume.setMaximumWidth(150)
    #self.volume.sliderMoved.connect(self.volume_change)
    self.volume.sliderPressed.connect(self.volume_show_pressed)
    self.volume.sliderReleased.connect(self.volume_show_released)
    self.volume.valueChanged.connect(self.volume_clicked_change)
    self.volume.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    
    volume_layout.addWidget(self.low_label, 0,0)
    volume_layout.addWidget(self.volume, 0,1)
    volume_layout.addWidget(high_label, 0,2)
    
    #play/pause button control
    self.play_btn = QPushButton(QIcon(os.path.abspath(os.path.join(self.bundle_dir,"16px-Octicons-playback-play.svg.png"))), "", self)
    self.play_btn.setCheckable(True)
    self.play_btn.setProperty("control_btn", True)
    self.play_btn.setToolTip("Play")
    self.play_btn.pressed.connect(self.play)
    
    #stop/fast_forward/rewind controls
    self.stop = QPushButton(QIcon(os.path.abspath(os.path.join(self.bundle_dir,"Octicons-primitive-square.svg.png"))), "", self)
    self.stop.setProperty("control_btn", True)
    self.stop.setToolTip("Stop")
    self.stop.clicked.connect(self.stop_play)
    
    self.rewind = QPushButton(QIcon(os.path.abspath(os.path.join(self.bundle_dir,"24px-Octicons-playback-rewind.svg.png"))), "", self)
    self.rewind.setProperty("control_btn", True)
    self.rewind.setToolTip("Backwards")
    self.rewind.pressed.connect(self.play_rewind)
    self.rewind.released.connect(self.stop_rewind)
      
    self.fast_forward = QPushButton(QIcon(os.path.abspath(os.path.join(self.bundle_dir,"24px-Octicons-playback-fast-forward.svg.png"))), "", self)
    self.fast_forward.setProperty("control_btn", True)
    self.fast_forward.setToolTip("Forward")
    self.fast_forward.pressed.connect(self.play_fast_f)
    self.fast_forward.released.connect(self.stop_fast_f)
    
    #controls layout insertion
    controls.addLayout(volume_layout)
    controls.addWidget(self.rewind)
    controls.addWidget(self.play_btn)
    controls.addWidget(self.stop)
    controls.addWidget(self.fast_forward)
    layout.addLayout(controls)
    self.setLayout(layout)
  
  def play(self):
    if(not self.player.source().isEmpty()):
      if(self.play_btn.isChecked()):
        self.play_btn.setToolTip("Pause")
        self.play_btn.setIcon(QIcon(os.path.abspath(os.path.join(self.bundle_dir,"Octicons-playback-pause.svg.png"))))
        self.player.play()
      else:
        self.play_btn.setToolTip("Play")
        self.play_btn.setIcon(QIcon(os.path.abspath(os.path.join(self.bundle_dir,"16px-Octicons-playback-play.svg.png"))))
        self.player.pause()
  
  def volume_key_up(self):
    vol = self.audioOuput.volume()
    
    if(vol < 1):
      self.volume.setSliderPosition((vol*100)+1)
      self.audioOuput.setVolume(vol+0.01)
  
  def volume_key_down(self):
    vol = self.audioOuput.volume()
    
    if(vol > 0):
      if(vol <= 0.02):
        self.volume.setSliderPosition(0)
        self.audioOuput.setVolume(0)
        return
      #label will change due to slider changing positions
      self.volume.setSliderPosition((vol*100)-1)
      self.audioOuput.setVolume(vol-0.01)
  
  def volume_change(self, pos):
    #self.volume.setStatusTip("Volume: " + str(pos))
    self.low_label.setText(str(pos)+"%")
    self.audioOuput.setVolume(pos/100)
    #self.status_bar.showMessage("Volume: " + str(pos))
  
  def volume_clicked_change(self, value):
    self.low_label.setText(str(value)+"%")
    self.audioOuput.setVolume(value/100)
  
  def volume_show_pressed(self):
    self.low_label.setText(str(self.volume.value())+"%")
    self.audioOuput.setVolume(self.volume.value()/100)
    #self.status_bar.showMessage("Volume: " + str(self.volume.value()))
  
  def volume_show_released(self):
    self.status_bar.clearMessage()
  
  #runs when video is playing, changes the time stamps and moves the video slider
  def playing(self, pos):
    self.video_seek.setSliderPosition(pos)
    
    minutes = (pos/(1000 * 60)) % 60
    seconds = (pos/1000) % 60
    hours = (pos/(1000 * 60 * 60)) % 24
    
    if(len(str(math.floor(seconds)))>1):
      self.current_pos.setText(str(minutes)[0]+":"+str(math.floor(seconds)))
    else:
      self.current_pos.setText(str(minutes)[0]+":0"+str(math.floor(seconds)))

    if(pos == self.video_seek.maximum()):
      self.stop_play()
    
  def stop_play(self):
    self.play_btn.setIcon(QIcon(os.path.abspath(os.path.join(self.bundle_dir,"16px-Octicons-playback-play.svg.png"))))
    self.player.stop()
  
  #rewind by 5 seconds will keep going
  def play_rewind(self):
    minutes = (self.video_seek.sliderPosition()/(1000 * 60)) % 60
    seconds = (self.video_seek.sliderPosition()/1000) % 60
    hours = (self.video_seek.sliderPosition()/(1000 * 60 * 60)) % 24
    
    if(self.player.isSeekable()):
      if(hours == 0 and minutes == 0 and seconds <= (1000*5)):
        self.video_seek.setSliderPosition(0)
        self.player.setPosition(0)
      else:
        self.video_seek.setSliderPosition(self.video_seek.sliderPosition() - (self.auto_seek*1000))
        self.player.setPosition(self.player.position() - (self.auto_seek*1000))
    
    minutes = (self.video_seek.sliderPosition()/(1000 * 60)) % 60
    seconds = (self.video_seek.sliderPosition()/1000) % 60
    hours = (self.video_seek.sliderPosition()/(1000 * 60 * 60)) % 24
    
    if(len(str(math.floor(seconds)))>1):
      self.current_pos.setText(str(minutes)[0]+":"+str(math.floor(seconds)))
    else:
      self.current_pos.setText(str(minutes)[0]+":0"+str(math.floor(seconds)))
    
  #stop rewind upon releasing button
  def stop_rewind(self):
    if(self.player.isSeekable()):
      pass
  
  #fast forward by 5 seconds keep going
  def play_fast_f(self):
    minutes = (self.video_seek.sliderPosition()/(1000 * 60)) % 60
    seconds = (self.video_seek.sliderPosition()/1000) % 60
    hours = (self.video_seek.sliderPosition()/(1000 * 60 * 60)) % 24
    
    minutes2 = (self.video_seek.maximum()/(1000 * 60)) % 60
    seconds2 = (self.video_seek.maximum()/1000) % 60
    hours2 = (self.video_seek.maximum()/(1000 * 60 * 60)) % 24
    
    if(self.player.isSeekable()):
      if(minutes == minutes2 and seconds >= seconds2-5):
        self.video_seek.setSliderPosition(self.video_seek.maximum())
        self.player.setPosition(self.player.duration())
      else:
        self.video_seek.setSliderPosition(self.player.position() + (self.auto_seek * 1000))
        self.player.setPosition(self.player.position() + (self.auto_seek * 1000))

    minutes = (self.video_seek.sliderPosition()/(1000 * 60)) % 60
    seconds = (self.video_seek.sliderPosition()/1000) % 60
    hours = (self.video_seek.sliderPosition()/(1000 * 60 * 60)) % 24
    
    if(len(str(math.floor(seconds)))>1):
      self.current_pos.setText(str(minutes)[0]+":"+str(math.floor(seconds)))
    else:
      self.current_pos.setText(str(minutes)[0]+":0"+str(math.floor(seconds)))
    
  #stop fast forward upon releasing button
  def stop_fast_f(self):
    if(self.player.isSeekable()):
      pass
  
  #activates when video slider is moved by dragging the handle
  def video_move(self, pos):
    if(not self.seeking_started):
      self.player.positionChanged.disconnect(self.playing)
      self.seeking_started = True
      
    minutes = (pos/(1000 * 60)) % 60
    seconds = (pos/1000) % 60
    hours = (pos/(1000 * 60 * 60)) % 24
    
    if(len(str(math.floor(seconds)))>1):
      self.current_pos.setText(str(minutes)[0]+":"+str(math.floor(seconds)))
    else:
      self.current_pos.setText(str(minutes)[0]+":0"+str(math.floor(seconds)))
    
    self.player.setPosition(pos)
    
    #self.player.positionChanged.connect(self.playing)
    #print(current)
  
  #activates when handle is released from dragging, reactivates mediaplayer actions
  def seek_release(self):
    self.seeking_started = False
    self.player.positionChanged.connect(self.playing)
  
  def go_fullscreen(self):
    if(not self.videoWidget.isFullScreen()):
      self.videoWidget.setFullScreen(True)
  
  #key events are all here
  def toggle_fullscreen(self):
    if(not self.videoWidget.isFullScreen()):
      self.videoWidget.setFullScreen(True)
       
    elif(self.videoWidget.isFullScreen()):
      self.videoWidget.setFullScreen(False)
  
  def escape_fullscreen(self):
    if(self.videoWidget.isFullScreen()):
      self.videoWidget.setFullScreen(False)
  
  def space_play(self):
    if(not self.player.source().isEmpty()):
      if self.player.isPlaying():
        self.play_btn.setToolTip("Play")
        self.play_btn.setIcon(QIcon(os.path.abspath(os.path.join(self.bundle_dir,"16px-Octicons-playback-play.svg.png"))))
        self.player.pause()
      else:
        self.play_btn.setToolTip("Pause")
        self.play_btn.setIcon(QIcon(os.path.abspath(os.path.join(self.bundle_dir,"Octicons-playback-pause.svg.png"))))
        self.player.play()
