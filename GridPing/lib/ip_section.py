from PySide.QtGui import *
from PySide import QtCore
import sys, re, random

class IpSection(QWidget):
  """
  The main section of the GUI.
  Responsible for taking ip inputs in different modes, validating
  them (displaying error messages if necessary), and passing the results
  ready to be processed.
  """
  TEST_NOT_SELECTED = 0
  TEST_SINGLE_IP = 1
  TEST_IP_RANGE = 2
  class PingStartSignal(QtCore.QObject):
    ping_start_signal = QtCore.Signal(list) #emit a list of strings (ips)
  pss = PingStartSignal()
  pingStarted = pss.ping_start_signal
  
  class PingStopSignal(QtCore.QObject):
    ping_stop_signal = QtCore.Signal()
  psss = PingStopSignal()
  pingStopped = psss.ping_stop_signal
  
  def __init__(self, parent=None):
    super(IpSection, self).__init__()
    self.test_mode = self.TEST_NOT_SELECTED # field used to set validator for second ip if necessary
    self.ping_started = False
    #connect some signals
    self.pingStarted.connect(self.pingStartedHandler)
    #self.pingStopped.connect(self.pingStoppedHandler) ## the widget shouldn't react to stopping pinging until confirmed by the master
    label_ping_choice = QLabel("Ping Type")
    self.combobox_ping_choice = QComboBox()
    self.combobox_ping_choice.addItems(["-" * 20, "Single IP Ping Test", "Multi-IP Ping Test"])
    self.combobox_ping_choice.currentIndexChanged[int].connect(self.pingSelected)
    self.label_ip1 = QLabel("IP")
    self.lineedit_ip1 = IPLineEdit()
    self.label_ip2 = QLabel("Range End")
    self.lineedit_ip2 = IPLineEdit()
    self.btn_start_stop = QPushButton("Start Pinging")
    self.btn_start_stop.clicked.connect(self.startStopPinging)
    self.label_warning = QLabel()
    self.label_warning.setStyleSheet("""
    QLabel {font-size: 12px;
            color: rgb(185,0,14);
            font-weight:bold;}
    """)
    self.label_warning.setAlignment(QtCore.Qt.AlignLeft)
    #connect signals
    self.lineedit_ip1.editingFinished.connect(self.validateIP1)
    self.lineedit_ip2.editingFinished.connect(self.validateIP2)
    #hide what needs to
    self.label_ip1.hide()
    self.lineedit_ip1.hide()
    self.label_ip2.hide()
    self.lineedit_ip2.hide()
    #setup layout
    layout = QFormLayout()
    layout.addRow(label_ping_choice,self.combobox_ping_choice) #span 2 columns
    layout.addRow(self.label_ip1, self.lineedit_ip1)
    layout.addRow(self.label_ip2, self.lineedit_ip2)
    layout.addRow(self.btn_start_stop)
    #make a layout to fix the warning label alignment
    layout_warning = QHBoxLayout()
    layout_warning.addWidget(self.label_warning)
    layout.addRow(layout_warning)
    self.setLayout(layout)
    
  def pingSelected(self, index):
    if index == 0:
      self.test_mode = self.TEST_NOT_SELECTED
      self.label_ip1.hide()
      self.lineedit_ip1.hide()
      self.label_ip2.hide()
      self.lineedit_ip2.hide()
    elif index == 1:
      #show the first ip-input line. Hide the other line
      self.test_mode = self.TEST_SINGLE_IP
      self.label_ip1.setText("")
      self.label_ip1.show()
      self.label_ip1.setText("IP")
      self.lineedit_ip1.show()
      self.label_ip2.hide()
      self.lineedit_ip2.hide()
    elif index == 2:
      self.test_mode = self.TEST_IP_RANGE
      self.label_ip1.show()
      self.label_ip1.setText("Range Start")
      self.lineedit_ip1.show()
      self.label_ip2.show()
      self.lineedit_ip2.show()
  
  def validateIP1(self):
    """IP1 should just follow the guidelines for normal ips"""
    if self.test_mode != self.TEST_NOT_SELECTED: #maybe after the field judged invalid, the user chooses not to test
      text_ip1 = self.lineedit_ip1.text()
      text_ip1 = text_ip1.replace(' ', '') #remove spaces
      validator = IPValidator()
      result = validator.validate(text_ip1, 0)
      if result != QValidator.Acceptable:
        self.label_warning.setText("Please enter a valid IP")
        self.lineedit_ip1.setFocus()
        return False
      else:
        self.label_warning.setText('')
        return True
    else:
      return True
    
  def validateIP2(self):
    """IP2 should follow the guidelines of normal IPs, plus that
       it should match well with IP1"""
    if self.test_mode != self.TEST_NOT_SELECTED:
      """first check if the first ip is valid. Otherwise, validating second ip is useless.
         Also, this mitigates a recursive error, where both line edits fight over focus because
         both of them are invalid.
      """ 
      valid_ip1 = self.validateIP1()
      if valid_ip1:
        text_ip2 = self.lineedit_ip2.text().replace(' ', '')
        self.lineedit_ip2.setText(text_ip2)
        validator = SecondIPValidator(self.lineedit_ip1.text())
        result = validator.validate(text_ip2, 0)
        if result == QValidator.Invalid: #this comes from IPValidator superclass
          self.label_warning.setText("Please enter a valid IP")
          self.lineedit_ip2.setFocus()
          return False
        elif result == QValidator.Intermediate: #try a fixup
          fixup = validator.fixup(text_ip2)
          self.lineedit_ip2.setText(fixup)
          self.label_warning.setText('')
          return True
        else:
          self.label_warning.setText('')
          return True
      else:
        return False
      
  def startStopPinging(self):
    """
    The start/stop button handler.
    disable fields. maybe check their validation state first (should I?)
    """
    if not self.ping_started:
      if self.test_mode == self.TEST_NOT_SELECTED:
        self.label_warning.setText("Please choose a test mode first")
        self.combobox_ping_choice.setFocus()
      elif self.test_mode == self.TEST_SINGLE_IP:
        #test ip1
        if self.validateIP1():
          ips = [self.lineedit_ip1.text()]
          self.pingStarted.emit(ips)
      elif self.test_mode == self.TEST_IP_RANGE:
        #validate both IPs
        if self.validateIP2():
          text_ip1 = self.lineedit_ip1.text()
          pos_lastdot = text_ip1.rfind('.')
          header = text_ip1[:pos_lastdot+1]
          range_start = int(text_ip1[pos_lastdot+1:])
          text_ip2 = self.lineedit_ip2.text()
          #pos_lastdot is applicable to the second ip too
          range_end = int(text_ip2[pos_lastdot+1:]) 
          ips = []
          for i in range(range_start, range_end + 1): #inclusive
            ips.append(header + str(i))
          self.pingStarted.emit(ips)
          self.ping_started = True
          self.btn_start_stop.setText("Stop Pinging")
          self.updateFields()
    elif self.ping_started:
      self.pingStopped.emit()
      
  def pingStartedHandler(self, ips):
    self.btn_start_stop.setText("Stop Pinging")
    self.ping_started = True
    self.updateFields()
        
  def pingStoppedHandler(self):
    self.btn_start_stop.setText("Start Pinging")
    self.ping_started = False
    self.updateFields()
    
  def updateFields(self):
    if self.ping_started:
      for field in [self.combobox_ping_choice, self.lineedit_ip1,
                    self.lineedit_ip2]:
        field.setEnabled(False)
    else:
      for field in [self.combobox_ping_choice, self.lineedit_ip1,
                    self.lineedit_ip2]:
        field.setEnabled(True)
        
    
class IPLineEdit(QLineEdit):
  def __init__(self, parent=None):
    super(IPLineEdit, self).__init__(parent)
    self.setInputMask("000.000.000.000; ")
    self.setAlignment(QtCore.Qt.AlignCenter)
    
class IPValidator(QValidator):
  """
  Validates that an ip has 4 number groups and that each group is less
  than 256
  """
  UNFIXABLE = 0
  IP_OUT_OF_RANGE = 1
  HEADER_UNMATCH = 2
  END_INVALID = 3
  
  def __init__(self):
    super(IPValidator, self).__init__()
    
  def validate(self, ip, editPos):
    #zer0, no section can be larger than 255
    regexp = re.compile(r"(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})")
    match = regexp.match(ip)
    if not match:
      return QValidator.Invalid
    for group in match.groups():
      if int(group) > 255:
        return QValidator.Invalid
    return QValidator.Acceptable
    
    
class SecondIPValidator(IPValidator):
  def __init__(self, firstIP):
    self._first_ip = firstIP
    
  def validate(self, ip, editPos):
    initial = super(SecondIPValidator, self).validate(ip, editPos)
    if initial != QValidator.Acceptable:
      self.invalidation_reason = self.UNFIXABLE
      return initial
    #first, the first 3 sections must be identical
    pos_lastdot_ip1 = self._first_ip.rfind('.')
    header_ip1 = self._first_ip[:pos_lastdot_ip1]
    pos_lastdot_ip2 = ip.rfind('.')
    header_ip2 = ip[:pos_lastdot_ip2]
    if header_ip2 != header_ip1:
      self.invalidation_reason = self.HEADER_UNMATCH
      return QValidator.Intermediate
    #second, the fourth number must be higher
    last1 = int(self._first_ip[pos_lastdot_ip1+1:])
    last2 = int(ip[pos_lastdot_ip2+1:])
    if not last2 > last1:
      self.invalidation_reason = self.END_INVALID
      return QValidator.Intermediate
    return QValidator.Acceptable
  
  def fixup(self, ip):
    if self.invalidation_reason == self.UNFIXABLE:
      pass
    if self.invalidation_reason == self.END_INVALID or \
      self.invalidation_reason == self.HEADER_UNMATCH:
      #return the first 3 sections unchanged and the last randomly incremented
      pos_lastdot = self._first_ip.rfind('.')
      header_first = self._first_ip[:pos_lastdot+1]
      end_first = int(self._first_ip[pos_lastdot+1:])
      valid_end = min(random.choice(range(end_first, end_first+10)), 255)
      return header_first + str(valid_end)
      
if __name__ == "__main__":
  app = QApplication(sys.argv)
  main = IpSection()
  main.show()
  sys.exit(app.exec_())