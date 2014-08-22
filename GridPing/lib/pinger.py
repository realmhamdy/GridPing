from PySide.QtGui import QWidget, QPushButton, QLabel, QVBoxLayout, QApplication
import sys, time, random, pyping, numpy as np
from multiprocessing import Pipe
from lib.util import RequestData, ReplyData

class Pinger(object):
  """
  Takes a list if ips/hosts to ping, and sends the ping responses
  back into a passed-in pipe.
  It may not be necessary to have a pinger_process thread
  """
  def __init__(self, ipList, reqData, replyPipe, parent=None):
    super(Pinger, self).__init__()
    self._ips = ipList
    self.req_data = reqData
    self.reply_pipe = replyPipe

  def run(self):
    for dest in self._ips:
      """
      For each ip, make an aggregate of all packet responses and then send the
      aggregate to the pipe.
      """
      packets_sent = 0
      reply_data = ReplyData()
      while packets_sent < self.req_data.packet_count:
        r = pyping.ping(dest, count=1, packet_size=self.req_data.buf_size,
                        timeout=self.req_data.timeout)
        reply_data = reply_data + ReplyData(r.destination_ip, r.packet_size, r.avg_rtt, r.packet_lost)
        #now figure out how to send this response to the caller thread
        packets_sent += 1
        time.sleep(self.getDelay(self.req_data))
      self.reply_pipe.send(reply_data)
      #send a reply that indicates we are finished
      finish_reply = ReplyData(finalReply=True)
    self.reply_pipe.send(finish_reply)
    
  def getDelay(self, reqData):
    """
    Figures out the packet delay based on the delay value and distribution
    """
    #delay is in seconds... Right?. this is needed for time.sleep
    if reqData.distribution == RequestData.DISTRIBUTION_CONSTANT:
      return reqData.delay
    elif reqData.distribution == RequestData.DISTRIBUTION_UNIFORM:
      delay = random.uniform(0, reqData.delay) #uniformly random value between zero, request delay
    elif reqData.distribution == RequestData.DISTRIBUTION_GAUSSIAN:
      delay = np.random.normal(reqData.delay)
    elif reqData.distribution == RequestData.DISTRIBUTION_POISSON:
      delay = np.random.poisson(reqData.delay)
    elif reqData.distribution == RequestData.DISTRIBUTION_EXPONENTIAL:
      delay = np.random.exponential(reqData.delay)
    return delay

class PingerView(QWidget):
  def __init__(self, parent=None):
    super(PingerView, self).__init__(parent)
    self.state = 0
    layout = QVBoxLayout()
    self.btn_start_stop = QPushButton("Start Pinging")
    self.lbl_output = QLabel()
    self.btn_start_stop.clicked.connect(self.controlThread)
    layout.addWidget(self.btn_start_stop)
    layout.addWidget(self.lbl_output)
    self.setLayout(layout)
    
  def createPingerThread(self):
    req_data = RequestData(100, 1000, 1000, 3)
    self.receive_pipe, send_pipe =  Pipe(duplex=False)
    self.pinger_process = Pinger(["www.google.com"], req_data, send_pipe)

  def controlThread(self):
    if self.state == 0:
      self.createPingerThread()
      self.state = 1
      self.btn_start_stop.setText("Stop Pinging")
      self.pinger_process.start()
      data  = self.receive_pipe.recv()
      self.lbl_output.setText(str(data))
      self.pinger_process.terminate()
      self.pinger_process.wait()
      self.state = 0
      self.btn_start_stop.setText("Start Pinging")
      
if __name__ == "__main__":
  app = QApplication(sys.argv)
  main = PingerView()
  main.show()
  sys.exit(app.exec_())
