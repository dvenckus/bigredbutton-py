#
# Class TaskItem
#

from sqlalchemy import Column, Integer, String, Boolean, Sequence
from models.meta import Base
from models.unixtimestamp import UnixTimestamp
#import calendar
#import time
import json


########################################################################
class TaskItem(Base):
    """"""
    __tablename__ = "tasks"

    id = Column(Integer, Sequence('task_id_seq'), primary_key=True)
    timestamp = Column(UnixTimestamp)
    username = Column(String(25), default='')
    task = Column(String(25), default='')
    options = Column(String(256), default='')
    status = Column(Integer, default=0)

    parsedOptions = {}

    #----------------------------------------------------------------------
    def __init__(self, username, task, options={}, status=0):
      # timestamp in unixtime
      self.username = username
      self.task = task
      self.options = json.dumps(options)
      self.status = status

      self.parsedOptions = options


    def __repr__(self):
      return "<TaskItem(id='%d', task='%s', options='%s', username='%s', timestamp='%s', status='%d')>" % (
                    self.id, self.task, self.options, self.username, self.timestamp, self.status)


    def toDict(self):
      ''' convert object to dict '''
      dict_ = {}
      for key in self.__mapper__.c.keys():
          dict_[key] = getattr(self, key)
      return dict_


    def parseOptions(self):
      ''' parse options string into json dict '''
      self.parsedOptions = json.loads(self.options)
      return self.parsedOptions

