#
# Class UnixTimestamp
#
# custom Data Type for SqlAlchemy

from sqlalchemy import types
from datetime import datetime
from time import time
import pytz


class UnixTimestamp(types.TypeDecorator):
  impl = types.INTEGER

  def process_bind_param(self, value, dialect):
    ''' default timestamp to current unix timestamp on insert (ignore microseconds)'''
    return int(time())

  def process_result_value(self, value, dialect):
    ''' converts timestamp to local dateformat on select '''
    tz = pytz.timezone('America/Chicago')
    return datetime.fromtimestamp(value, tz).strftime('%Y-%m-%d %H:%M:%S')
