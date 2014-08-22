from __future__ import division
import os, ctypes, datetime

class RequestData(object):
  DISTRIBUTION_CONSTANT = 0
  DISTRIBUTION_UNIFORM = 1
  DISTRIBUTION_GAUSSIAN = 2
  DISTRIBUTION_POISSON = 3
  DISTRIBUTION_EXPONENTIAL = 4
  def __init__(self, buffSize, timeOut, delay, packetCount, distribution=DISTRIBUTION_CONSTANT):
    self.buf_size = buffSize
    self.timeout = timeOut
    self.delay = delay
    self.packet_count = packetCount
    self.distribution = distribution
    
  def __str__(self):
    return "<RequestData buffSize={} timeOut={} delay={} packetCount={} distribution=%s >".\
             format(self.buf_size, self.timeout, self.delay, self.packet_count, self.distribution)
    

class ReplyData(object):
  """
  Carries the reply data from the pinger thread to the gui thread.
  Responsible for correct message content and formatting, based on reply data.
  """
  def __init__(self, dest='', size=0, rtt=0, packetsLost=0, finalReply=False):
    self.date = datetime.datetime.now().strftime("%Y-%m-%d %I-%M-%S%p")
    self.dest = dest
    self.size = size
    try:
      self.rtt = float(rtt) #rtt is returned from the pyping library as a string, None in failure
    except TypeError:
      self.rtt = 0
    self.packets_lost = packetsLost
    self.final_reply = finalReply

  def __add__(self, other):
    dest = self.dest if len(self.dest) > len(other.dest) else other.dest
    size = self.size + other.size
    rtt = self.rtt + other.rtt
    packets_lost = self.packets_lost + other.packets_lost
    final_reply = self.final_reply or other.final_reply
    return ReplyData(dest, size, rtt, packets_lost, final_reply)
  
  def __str__(self):
    if self.packets_lost > 0:
      return "{} Reply from {} Request timed out".format(self.date,
                              self.dest)
    return "{} Reply from {} bytes={} time={}ms".format(self.date,
                              self.dest, self.size, self.rtt)
    
class SummaryData(object):
  """
  Data collected to put in the summary section
  """
  def __init__(self, sentPackets, receivedPackets, outputDelay):
    self.sent_packets = sentPackets
    self.received_packets = receivedPackets
    self.packets_lost = self.sent_packets - self.received_packets
    try:
      self.loss_percentage = self.packets_lost / self.sent_packets * 100
    except ZeroDivisionError:
      self.loss_percentage = 0
    self.output_delay = outputDelay
    

def isAdminCurrent():
  try:
    return os.getuid() == 0
  except AttributeError:
    return ctypes.windll.shell32.IsUserAnAdmin() != 0