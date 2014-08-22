from PySide.QtGui import QWidget, QLabel, QComboBox, QSpinBox, QFormLayout,\
      QValidator, QAbstractSpinBox, QApplication
import sys
from lib.util import RequestData

class OptionSection(QWidget):
  """
  Collects options and returns proper representation when requested
  """
  def __init__(self, parent=None):
    super(OptionSection, self).__init__(parent)
    #create widgets
    label_buffer_size = QLabel("Buffer Size")
    self.spinbox_buffer_size = ValidatedSpinBox()
    self.spinbox_buffer_size.setSingleStep(10)
    self.spinbox_buffer_size.setMaximum(9999999)
    self.spinbox_buffer_size.setSuffix(" bytes")
    self.spinbox_buffer_size.setValue(55)
    label_timeout = QLabel("Timeout")
    self.spinbox_timeout = ValidatedSpinBox()
    self.spinbox_timeout.setMaximum(9999999)
    self.spinbox_timeout.setSuffix(" ms")
    self.spinbox_timeout.setSingleStep(100)
    self.spinbox_timeout.setValue(1000)
    label_delay = QLabel("Delay Between Packets")
    self.spinbox_delay = ValidatedSpinBox()
    self.spinbox_delay.setMaximum(9999999)
    self.spinbox_delay.setSuffix(" ms")
    self.spinbox_delay.setSingleStep(100)
    self.spinbox_delay.setValue(1000)
    label_delay_distribution = QLabel("Delay Distribution")
    self.combobox_delay_distribution = QComboBox()
    self.combobox_delay_distribution.addItem("Constant")
    self.combobox_delay_distribution.insertSeparator(10)
    self.combobox_delay_distribution.addItems(["Uniform", "Gaussian", "Poisson", "Exponential"])
    label_packet_count = QLabel("Packets to Send")
    self.spinbox_packet_count = ValidatedSpinBox()
    self.spinbox_packet_count.setMaximum(9999999)
    self.spinbox_packet_count.setValue(3)
    #setup layout
    layout = QFormLayout()
    layout.addRow(label_buffer_size, self.spinbox_buffer_size)
    layout.addRow(label_timeout, self.spinbox_timeout)
    layout.addRow(label_delay, self.spinbox_delay)
    layout.addRow(label_delay_distribution, self.combobox_delay_distribution)
    layout.addRow(label_packet_count, self.spinbox_packet_count)
    self.setLayout(layout)
    
  def getOptions(self):
    """
    Return a RequestData object representing selected options
    """
    buf_size = self.spinbox_buffer_size.value()
    timeout = self.spinbox_timeout.value()
    delay = self.spinbox_delay.value() / 1000
    packet_count = self.spinbox_packet_count.value()
    selected_distribution = self.combobox_delay_distribution.currentIndex()
    if selected_distribution == 0:
      distribution = RequestData.DISTRIBUTION_CONSTANT
    elif selected_distribution == 1:
      distribution = RequestData.DISTRIBUTION_UNIFORM
    elif selected_distribution == 2:
      distribution = RequestData.DISTRIBUTION_GAUSSIAN
    elif selected_distribution == 3:
      distribution = RequestData.DISTRIBUTION_POISSON
    elif selected_distribution == 4:
      distribution = RequestData.DISTRIBUTION_EXPONENTIAL
    
    return RequestData(buf_size, timeout, delay, packet_count, distribution)
  
  def disableWidgets(self):
    for widget in [self.spinbox_buffer_size, self.spinbox_delay,
                   self.spinbox_packet_count, self.spinbox_timeout, 
                   self.combobox_delay_distribution]:
      widget.setEnabled(False)
  
  def enableWidgets(self):
    for widget in [self.spinbox_buffer_size, self.spinbox_delay,
                   self.spinbox_packet_count, self.spinbox_timeout, 
                   self.combobox_delay_distribution]:
      widget.setEnabled(True)
        
class ValidatedSpinBox(QSpinBox):
  """
  Uses validation and correction mode to refuse empty inputs in a nice way
  PS : doesn't work as expected!
  """
  
  def __init__(self, parent=None):
    super(ValidatedSpinBox, self).__init__(parent)
    self.setCorrectionMode(QAbstractSpinBox.CorrectToPreviousValue)
  
  def validate(self, value, *args):
    if len(str(value)) == 0:
      return QValidator.Intermediate
    else:
      return QValidator.Acceptable
    
if __name__ == "__main__":
  app = QApplication(sys.argv)
  main = OptionSection()
  main.show()
  sys.exit(app.exec_())