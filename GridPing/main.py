from PySide.QtCore import *
from PySide.QtGui import *
import sys
from multiprocessing import Pipe, Process
from lib.ip_section import IpSection
from lib.pinger import Pinger
from lib.summary_section import SummarySection
from lib.option_section import OptionSection


class MasterWindow(QMainWindow):
  """
  Manages the general layout and event propagation through
  the gui. (pulls the strings :])
  """
  def __init__(self, parent=None):
    super(MasterWindow, self).__init__(parent)
    #setup the ip section
    self.ip_section = IpSection()
    self.ip_section.pingStarted.connect(self.startPinging)
    self.ip_section.pingStopped.connect(self.endPinging)
    #other sections
    self.option_section = OptionSection()
    self.summary_section = SummarySection()
    #setup layout
    layout = QGridLayout()
    #groupbox for the ip section
    groupbox_ip_section = QGroupBox()
    #dummy layout for the groupbox
    groupbox_ip_section_layout = QVBoxLayout()
    groupbox_ip_section_layout.addWidget(self.ip_section)
    groupbox_ip_section.setLayout(groupbox_ip_section_layout)
    groupbox_ip_section.setTitle("Configure Tests")
    #ditto for the option section
    groupbox_option_section = QGroupBox()
    groupbox_option_section.setTitle("Configure Request Options")
    groupbox_option_section_layout = QVBoxLayout()
    groupbox_option_section_layout.addWidget(self.option_section)
    groupbox_option_section.setLayout(groupbox_option_section_layout)
    row = 0; col = 0;
    layout.addWidget(groupbox_ip_section, 0, 0)
    col += 1
    layout.addWidget(groupbox_option_section, row, col)
    layout.setRowMinimumHeight(1, 75) #some spacing between top and bottom
    row += 2; col -= 1
    layout.addWidget(self.summary_section, row, col, 1, 2)
    #some private fields
    self.pinging_started = False
    self.ping_ips = [] #to display them in the status bar
    self.ping_index = 0
    #dummy layout widget
    widget = QWidget()
    widget.setLayout(layout)
    self.setCentralWidget(widget)
    #setup a poll timer
    self._timer = QTimer()
    self._timer.setInterval(1000)
    self._timer.timeout.connect(self.pollReplyPipe)
    #setup the status bar
    self.lbl_status = QLabel()
    self.lbl_status.setStyleSheet("""
      QLabel {color:rgb(57, 77, 249);
              font-style:italic;
              font-family: "Segoe UI, Tahoma, sans-serif";
              font-size:13px;}
    """)
    self.progressbar_pinging = QProgressBar()
    self.progressbar_pinging.setTextVisible(False)
    self.progressbar_pinging.setMaximumHeight(15)
    self.progressbar_pinging.setMaximumWidth(100)
    self.statusBar().addWidget(self.lbl_status)
    self.statusBar().addPermanentWidget(self.progressbar_pinging) #this should also show the status bar
    self.setWindowTitle("Smart Ping v1.11")
    
  def startPinging(self, ips):
    self.pinging_started = True
    self.ping_index = 0
    self.ping_ips = ips
    self.progressbar_pinging.reset()
    self.progressbar_pinging.setMinimum(0)
    self.progressbar_pinging.setMaximum(len(ips))
    self.summary_section.setIPs(ips)
    self.option_section.disableWidgets()
    self.receive_pipe, send_pipe = Pipe(duplex=False)
    self.request_data = self.option_section.getOptions()
    self.pinger = Pinger(ips, self.request_data, send_pipe) 
    self.pinger_process = Process(target=self.pinger.run)
    self.pinger_process.start()
    self.lbl_status.setText("Pinging %s ..." % ips[0])
    self.ping_index += 1
    self._timer.start()
    
  def pollReplyPipe(self):
    while self.receive_pipe.poll():
      reply_data = self.receive_pipe.recv() 
      if reply_data.final_reply: #pinging finished
        self._timer.stop()
        self.pinger_process.terminate()
        self.pinger_process.join()
        self.pinging_started = False # positioning this is crucial before emitting the signal
        self.ip_section.pingStoppedHandler()
        self.option_section.enableWidgets()
        self.lbl_status.setText("Done")
      else: 
        self.summary_section.takeReplyData(reply_data, self.request_data.packet_count)
        try: #because indexing will fail in after the last IP.We index 1 IP ahead of requests
          self.lbl_status.setText("Pinging %s ..." % self.ping_ips[self.ping_index])
        except IndexError:
          pass
        self.ping_index += 1
      self.progressbar_pinging.setValue(self.progressbar_pinging.value() + 1)
    
  def endPinging(self):
    if self.pinging_started:
      msg_box = QMessageBox()
      msg_box.setWindowTitle("Confirm")
      msg_box.setIcon(QMessageBox.Question)
      msg_box.setText("Operation still running")
      msg_box.setInformativeText("Are you sure you want to stop it?")
      msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
      resp = msg_box.exec_()
      if resp == QMessageBox.Yes:
        #enable buttons (common function), display summaries
        self.pinger_process.terminate()
        self.pinger_process.join()
        self.pinging_started = False
        self.ip_section.pingStoppedHandler()
        self.option_section.enableWidgets()
        self.summary_section.pingingStoppedHandler()
        self.lbl_status.setText("")
      else:
        pass

if __name__ == "__main__":
  app = QApplication(sys.argv)
  main = MasterWindow()
  main.show()
  sys.exit(app.exec_())