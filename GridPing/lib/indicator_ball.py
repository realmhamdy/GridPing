from PySide.QtCore import *
from PySide.QtGui import *
import sys

class BallWidget(QWidget):
  PENDING = 0
  REACHABLE = 1
  UNREACHABLE = 2
  INACTIVE = 3
  def __init__(self, ip, parent=None):
    """
    ip -- string that indicates the ip to display as a tooltip
    Indicator for ping states
    gray -- pending
    red -- unreachable
    green -- reachable
    This widget is resizable, but preferably small
    """
    super(BallWidget, self).__init__(parent)
    self.setMouseTracking(True)
    self.mouse_over = False
    self.ip = ip
    self.setState(self.PENDING)
    
  def mouseMoveEvent(self, me):
    if not self.mouse_over:
      self.mouse_over = True
      self.repaint()
    
  def leaveEvent(self, le):
    self.mouse_over = False
    self.repaint()

  def paintEvent(self, pe):
    painter = QPainter(self)
    w = self.width()
    h = self.height()
    gradient = QRadialGradient(w/4, h/6, 50) #the color goes from the gradient focal point to the center point
    gradient.setFocalPoint(w/3, h/4)
    gradient.setColorAt(0, Qt.white)
    if self._state == self.INACTIVE:
      gradient.setColorAt(1, Qt.black)
    if self._state == self.PENDING:
      gradient.setColorAt(1, Qt.yellow)
    elif self._state == self.REACHABLE:
      gradient.setColorAt(1, Qt.green)
    elif self._state == self.UNREACHABLE:
      gradient.setColorAt(1, Qt.red)
    brush = QBrush(gradient)
    painter.setBrush(brush)
    if self.mouse_over:
      pen = QPen(Qt.black)
    else:
      pen = QPen(Qt.gray)
    painter.setPen(pen)
    painter.drawEllipse(0, 0, w-2, h-2) #-2 so that the border appears unclipped
   
  def getState(self):
    return self._state
    
  def setState(self, state):
    self._state = state
    if state == self.PENDING:
      state_str = "Pending"
    if state == self.REACHABLE:
      state_str = "Ok"
    if state == self.UNREACHABLE:
      state_str = "Unreachable"
    if state == self.INACTIVE:
      state_str = "Cancelled"
    self.setToolTip("{} -- {}".format(self.ip, state_str))
    self.repaint()
    
  state = property(getState, setState)

if __name__ == "__main__":
  app = QApplication(sys.argv)
  main = BallWidget()
  main.show()
  sys.exit(app.exec_())
