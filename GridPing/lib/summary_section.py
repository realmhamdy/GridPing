from PySide.QtGui import QWidget, QTabWidget, QTextEdit, QLabel, QFrame, QVBoxLayout
from PySide.QtGui import QHBoxLayout, QFormLayout, QGridLayout, QStackedLayout
from lib.dynamic_grid import BallGrid
from lib.indicator_ball import BallWidget
from lib.util import SummaryData

class SummarySection(QTabWidget):
  """
  Represents the summary section.
  Takes reply data from main ui and updates it's tabs
  Keeps track of cumulative summary data.
  """
  def __init__(self, parent=None):
    super(SummarySection, self).__init__(parent)
    self.text_edit_summary = QTextEdit()
    self.text_edit_summary.setReadOnly(True)
    self.addTab(self.text_edit_summary, "Output")
    self.ball_grid = BallGrid(30, 30, 2)
    self.addTab(self.ball_grid, "Led View")
    self.tab_summary = SummaryTab()
    self.addTab(self.tab_summary, "Summary")
    #some private fields, keep track of accumulated summary data
    self.current_ip = 0 #we take reply data for ips in order
    self.sent_packets = 0
    self.received_packets = 0
    self.average_delay = 0
    
  def setIPs(self, ips):
    #this indicates the start of a new ping, could be treated
    #as a pingStarted signal
    self.current_ip = 0
    self.sent_packets = 0
    self.received_packets = 0
    self.average_delay = 0
    self.text_edit_summary.clear()
    self.ball_grid.layoutForIps(ips)
    self.tab_summary.zeroOut()
  
  def takeReplyData(self, replyData, sentPackets): #sent packets is passed in as extra
    """
    Update the output text area with the replyData string representation
    Set proper widget states on the BallGrid
    Calculate summaries cumulatively and set them for display on the summary tab 
    """
    self.text_edit_summary.append(str(replyData))
    packets_lost = replyData.packets_lost
    if packets_lost:
      self.ball_grid.setStateAt(self.current_ip, BallWidget.UNREACHABLE)
    else:
      self.ball_grid.setStateAt(self.current_ip, BallWidget.REACHABLE)
    self.current_ip += 1
    self.sent_packets += sentPackets 
    self.received_packets = self.sent_packets - replyData.packets_lost
    self.average_delay += (replyData.rtt / self.current_ip) #the current_ip reflects the overall number of replies
    summary_data = SummaryData(self.sent_packets, self.received_packets, self.average_delay)
    self.tab_summary.setSummaryData(summary_data)
    
  def pingingStoppedHandler(self):
    self.ball_grid.pingingCancelledHandler()
  
class SummaryTab(QWidget):
  """
  Represents the ping output in a numeric format
  """
  def __init__(self, parent=None):
    super(SummaryTab, self).__init__(parent)
    #create the widgets
    self.label_info = QLabel("No summary data to display")
    label_sent_packets = QLabel("Sent Packet Count")
    self.label_sent_packets = StyledLabel()
    self.label_sent_packets.setMaximumHeight(30)
    label_received_packets = QLabel("Received Packet Count")
    self.label_received_packets = StyledLabel()
    self.label_received_packets.setMaximumHeight(30)
    label_packets_lost = QLabel("Packets Lost")
    self.label_packets_lost = StyledLabel()
    self.label_packets_lost.setMaximumHeight(30)
    label_loss_percentage = QLabel("Packet Loss Percentage")
    self.label_loss_percentage = StyledLabel()
    self.label_loss_percentage.setMaximumHeight(30)
    label_output_delay = QLabel("Average Output Delay")
    self.label_output_delay = StyledLabel()
    self.label_output_delay.setMaximumHeight(30)
    #setup summary_layout
    #first, setup a stacked summary_layout to indicate first there's no summary data
    self.layout_stack = QStackedLayout()
    summary_centerer_layout = QHBoxLayout()
    summary_layout = QGridLayout() #if I use formlayout, i'm afraid things will stretch out too much horizontally
    row = 1; col = 0;
    summary_layout.addWidget(label_sent_packets, row, col)
    col += 2
    summary_layout.addWidget(self.label_sent_packets, row, col) #leave a middle column empty
    row += 1; col -= 2;
    summary_layout.addWidget(label_received_packets, row, col)
    col += 2
    summary_layout.addWidget(self.label_received_packets, row, col)
    row += 1; col -= 2
    summary_layout.addWidget(label_packets_lost, row, col)
    col += 2
    summary_layout.addWidget(self.label_packets_lost, row, col)
    row += 1; col -= 2;
    summary_layout.addWidget(label_loss_percentage, row, col)
    col += 2
    summary_layout.addWidget(self.label_loss_percentage, row, col)
    row += 1; col -= 2;
    summary_layout.addWidget(label_output_delay, row, col)
    col += 2
    summary_layout.addWidget(self.label_output_delay, row, col)
    #center things out
    summary_layout.setColumnMinimumWidth(1, 100) # 100 pixels in the middle
    summary_layout.setRowMinimumHeight(0, 10) #100 pixels from top
    summary_centerer_layout.addStretch()
    summary_centerer_layout.addLayout(summary_layout)
    summary_centerer_layout.addStretch()
    #make a dump widget for the stacked summary_layout
    widget = QWidget()
    widget.setLayout(summary_centerer_layout)
    self.layout_stack.insertWidget(0, widget)
    #setup summary_layout for info label!
    layout_info_label = QVBoxLayout()
    layout_info_label.addStretch()
    layout_info_label.addWidget(self.label_info)
    layout_info_label.addStretch()
    #make dump widget for info label summary_layout!!
    widget_info_label = QWidget()
    widget_info_label.setLayout(layout_info_label)
    self.layout_stack.insertWidget(1, widget_info_label)
    self.setLayout(self.layout_stack)
    self.zeroOut()
    
  def setSummaryData(self, summaryData):
    self.label_sent_packets.setText(str(summaryData.sent_packets))
    self.label_received_packets.setText(str(summaryData.received_packets))
    self.label_packets_lost.setText(str(summaryData.packets_lost))
    self.label_loss_percentage.setText("%.2f %%" % summaryData.loss_percentage)
    self.label_output_delay.setText("%.2f ms" % summaryData.output_delay)
    self.layout_stack.setCurrentIndex(0)
    
  def zeroOut(self):
    #set all summary fields to their defaults
    self.setSummaryData(SummaryData(0, 0, 0))
    self.layout_stack.setCurrentIndex(1)
    
class StyledLabel(QLabel):
  def __init__(self, parent=None):
    super(StyledLabel, self).__init__(parent)
    self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)