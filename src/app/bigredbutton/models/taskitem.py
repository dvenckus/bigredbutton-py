#
# Class TaskItem
#

from sqlalchemy import Column, Integer, String, Boolean, Sequence
from models.meta import Base
from models.unixtimestamp import UnixTimestamp
#import calendar
#import time


########################################################################
class TaskItem(Base):
    """"""
    __tablename__ = "tasks"

    id = Column(Integer, Sequence('task_id_seq'), primary_key=True)
    timestamp = Column(UnixTimestamp)
    username = Column(String(25), default='')
    subdomain = Column(String(25), default='')
    site = Column(String(10), default='')
    task = Column(String(25), default='')
    dbbackup = Column(Boolean, default=False)
    status = Column(Integer, default=0)

    #----------------------------------------------------------------------
    def __init__(self, username, subdomain, site, task, dbbackup, status=0):
        """"""
        # timestamp in unixtime
        self.username = username
        self.subdomain = subdomain
        self.site = site
        self.task = task
        self.dbbackup = dbbackup
        self.status = status

    def __repr__(self):
        return "<TaskItem(id='%d', subdomain='%s', site='%s', task='%s', backup='%r', username='%s', timestamp='%s', status='%d')>" % (
                     self.id, self.subdomain, self.site, self.task, self.dbbackup, self.username, self.timestamp, self.status)

    def toDict(self):
      dict_ = {}
      for key in self.__mapper__.c.keys():
          dict_[key] = getattr(self, key)
      return dict_
