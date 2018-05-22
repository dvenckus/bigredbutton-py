#
# Class TaskItem
#

from sqlalchemy import Column, Integer, String, Boolean, Sequence
from flask import jsonify
from models.meta import Base, BaseItem
from models.unixtimestamp import UnixTimestamp


########################################################################
class TaskItem(Base, BaseItem):
    """"""
    __tablename__ = "tasks"

    id = Column(Integer, Sequence('task_id_seq'), primary_key=True)
    timestamp = Column(UnixTimestamp)
    username = Column(String(25), default='')
    task = Column(String(25), default='')
    options = Column(String(256), default='')
    status = Column(Integer, default=0)

    #----------------------------------------------------------------------
    def __init__(self, username, task, options='', status=0):
      '''
      timestamp in unixtime using unixtimestamp decorator
      options are expected in the form of a json-compatible string
      '''
      self.username = username
      self.task = task
      self.options = options
      self.status = status


    def __repr__(self):
      return "<TaskItem(id='%d', task='%s', options='%s', username='%s', timestamp='%s', status='%d')>" % (
                    self.id, self.task, self.options, self.username, self.timestamp, self.status)


