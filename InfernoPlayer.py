from PySide6.QtWidgets import QApplication
from player import MPlayer

if __name__ == "__main__":
  
  app = QApplication([])
  
  window = MPlayer()
  window.show()
  
  app.exec()
  #widget = MyWidget()
  #widget.resize(800,800)
  #widget.show()
  #sys.exit(app.exec())
