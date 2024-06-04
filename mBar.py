from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtCore import Qt

class MenuBar(QWidget):
  def __init__(self):
    super().__init__()
    
    self.version_msg = QMessageBox()
    self.source_msg = QMessageBox()
    self.keys_msg = QMessageBox()
    self.screenshot_msg = QMessageBox()
    self.owner_msg = QMessageBox()
  
  def show_screenshot_msg(self, msg):
    message = f"Screenshot saved in current directory:\n\n{msg}"
    self.screenshot_msg.information(self, "Screenshot", message, QMessageBox.Ok)

  def show_true_owner(self):
    message = """
    This is the property of InfernoCycle.
    For more projects from me please visit my github at
    https://github.com/InfernoCycle"""
    self.owner_msg.information(self, "Owner", message, QMessageBox.Ok)
  
  def show_keys(self):
    message = """
    Play/Pause = Spacebar\n
    Fast Forward = Right Arrow\n
    Backward = Left Arrow\n
    Fullscreen = f\n
    Volume Up = Up Arrow\n
    Volume Down = Down Arrow \n
    Screenshot = s
    """
    self.keys_msg.information(self, "Shortcuts", message, QMessageBox.Ok)
