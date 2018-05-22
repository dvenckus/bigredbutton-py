#
# Class TaskHistory
#

from sqlalchemy import Column, Integer, String, Text, Boolean, Sequence
from models.meta import Base
from models.unixtimestamp import UnixTimestamp
#import calendar
#import time
import json



########################################################################
class TaskHistoryItem(Base):
    """"""
    __tablename__ = "task_history"

    id = Column(Integer, Sequence('task_id_seq'), primary_key=True)
    timestamp = Column(UnixTimestamp)
    username = Column(String(25), default='')
    task = Column(String(25), default='')
    options = Column(String(256), default='')
    result = Column(Text, default='')

    parsedOptions = {}

    #----------------------------------------------------------------------
    def __init__(self, username, task, options='', result=''):
      '''
      timestamp in unixtime using unixtimestamp decorator
      options are expected in the form of a json-compatible string
      '''
      self.username = username
      self.task = task
      self.options = options
      self.result = result

      #self.parsedOptions()


    def __repr__(self):
      return "<TaskHistoryItem(id='%d', task='%s', options='%s', username='%s', timestamp='%s', result='%s')>" % (
                    self.id, self.task, self.options, self.username, self.timestamp, self.result)


    def toDict(self):
      ''' convert object to dict '''
      dict_ = {}
      for key in self.__mapper__.c.keys():
          dict_[key] = getattr(self, key)
      return dict_


    def parseOptions(self):
      ''' 
      parse options string into json dict 
      call json.loads 2x to handle improperly quoted strings; 
      1st call converts to json-compatible string
      2nd call, if necessary, converts to json dict
      '''
      #self.parsedOptions = json.loads(json.loads(self.options))
      json_obj = json.loads(self.options)
      if isinstance(json_obj, str):
        # problem with json, call loads again
        json_obj = json.loads(json_obj)
        
      self.parsedOptions = json_obj
      return self.parsedOptions
