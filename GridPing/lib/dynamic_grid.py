from __future__ import division
from PySide.QtGui import *
from PySide.QtCore import *
import sys, math
from lib.indicator_ball import BallWidget


class GridWidget(QWidget):
  def __init__(self, widgetWidth, widgetHeight, layoutSpacing,
               parent=None):
    """
    A grid that has widget(s) with fixed size. It responds
    to resizing, adding or removing rows to keep the widget's
    size constant and spacing, too.
    """
    super(GridWidget, self).__init__(parent)
    self._widgets = []
    self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.ww = widgetWidth
    self.wh = widgetHeight
    self.ls = layoutSpacing
    self.widgets_in_row = 0
    self.grid = QGridLayout()
    self.grid.setHorizontalSpacing(layoutSpacing)
    self.grid.setVerticalSpacing(layoutSpacing)
    self.setLayout(self.grid)

  def addWidget(self, widget):
    widget.setFixedWidth(self.ww)
    widget.setFixedHeight(self.wh)
    self._widgets.append(widget)
    
  def widgets(self):
    return self._widgets
  
  def clear(self):
    for widget in self._widgets:
      self.grid.removeWidget(widget)
      widget.deleteLater()
    self._widgets = []

  def resizeEvent(self, re):
    if not len(self._widgets):
      return #no widgets, don't do anything (eliminates a division by zero error)
    #recalculate rows based on current width
    w = self.width()
    #get the number of widgets that can be inserted per row
    hor_distance = 0
    n = 0 #the number of widgets that can be inserted in a row
    while hor_distance < w:
      hor_distance += self.ww
      hor_distance += self.ls
      n += 1
    if hor_distance > w:
      n -= 1
    n = min(n, len(self._widgets))
    self.widgets_in_row = n
    if self.grid.rowCount():
      for widget in self._widgets: #remove all widgets
        self.grid.removeWidget(widget)
      self.grid.update()
    row = 0; col = 0;
    grid_row_count = int(math.ceil(len(self._widgets) / n)) #might leave the last row incomplete
    widget_grid = self.redimArray(self._widgets, grid_row_count, n)
    #insert the widgets
    for widget_row in widget_grid:
      for widget in widget_row:
        self.grid.addWidget(widget, row, col)
        col += 1
      row += 1
      col = 0

  def redimArray(self, array, rows, cols):
    """array is a flat list"""
    #this function is available in numpy, but I don't want to introduce
    #another dependency
    complete_rows = rows
    if rows * cols > len(array):
      complete_rows = int(math.floor(len(array) / cols))
    res = []
    for irow in range(complete_rows):
      row = []
      for icol in range(cols):
        row.append(array[irow*cols+icol])
      res.append(row)
    if complete_rows < rows: #add the last incomplete row
      start_index = complete_rows * cols
      last_row = array[start_index:]
      res.append(last_row)
    return res
  
  def setStateAt(self, i, state):
    self._widgets[i].state = state
  

class NotifierScrollArea(QScrollArea):
  """
  Scroll area that notifies it's widget when resized
  """
  def __init__(self, parent=None):
    super(NotifierScrollArea, self).__init__(parent)

  def resizeEvent(self, re):
    self.widget().resize(self.size())
    
class DynamicGrid(QWidget):
  def __init__(self,  widgetWidth=30, widgetHeight=30, layoutSpacing=2, 
               parent=None):
    super(DynamicGrid, self).__init__(parent)
    self.grid_widget = GridWidget(widgetWidth, widgetHeight, layoutSpacing)
    scroll_area = NotifierScrollArea()
    scroll_area.setWidget(self.grid_widget)
    layout = QVBoxLayout()
    layout.addWidget(scroll_area)
    self.setLayout(layout)
  
  def addWidget(self, w, *args, **kwargs):
    self.grid_widget.addWidget(w, *args, **kwargs)
    
  def clear(self):
    self.grid_widget.clear()
    
class BallGrid(DynamicGrid):
  def __init__(self, ballWidth, ballHeight, spacing, parent=None):
    super(BallGrid, self).__init__(ballWidth, ballHeight, spacing, parent)
    
  def setStateAt(self, i, state):
    self.grid_widget.setStateAt(i, state)
    
  def layoutForIps(self, ips):
    self.clear()
    for ip in ips:
      bw = BallWidget(ip)
      self.addWidget(bw)
    #instead of resize() once, which doesn't always trigger resizing
    self.grid_widget.resize(self.size() + QSize(0, 1))
    self.grid_widget.resize(self.size() + QSize(0, -1))
    
  def pingingCancelledHandler(self):
    """
    Set all the balls that have state as pending to cancelled
    """
    for ball in self.grid_widget.widgets():
      if ball.state == BallWidget.PENDING:
        ball.setState(BallWidget.INACTIVE)

if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = BallGrid(30, 30, 1)
  ips = ["the ip" for i in range(25)]
  window.layoutForIps(ips)
  window.setMinimumSize(100, 100)
  window.show()
  sys.exit(app.exec_())
