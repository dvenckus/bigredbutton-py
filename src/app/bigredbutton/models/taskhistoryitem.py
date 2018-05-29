#
# Class TaskHistory
#

from sqlalchemy import Column, Integer, String, Text, Boolean, Sequence
from models.meta import Base, BaseItem
from models.unixtimestamp import UnixTimestamp



########################################################################
class TaskHistoryItem(Base, BaseItem):
    """"""
    __tablename__ = "task_history"

    id = Column(Integer, Sequence('task_id_seq'), primary_key=True)
    timestamp = Column(UnixTimestamp)
    username = Column(String(25), default='')
    task = Column(String(25), default='')
    options = Column(String(256), default='')
    result = Column(Text, default='')

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


    def __repr__(self):
      return "<TaskHistoryItem(id='%d', task='%s', options='%s', username='%s', timestamp='%s', result='%s')>" % (
                    self.id, self.task, self.options, self.username, self.timestamp, self.result)

