#
# Class PushItem
#
from models.meta import BaseItem
from time import time
from datetime import datetime
import pytz


########################################################################
class PushItem(BaseItem):
    """"""
    id = 0
    timestamp = 0
    username = ''
    task = ''
    options = ''
    status = 0

    #----------------------------------------------------------------------
    def __init__(self, username, task, options='', status=0):
        '''
        timestamp in unixtime using unixtimestamp decorator
        options are expected in the form of a json-compatible string
        '''
        self.timestamp = int(time())
        self.username = username
        self.task = task
        self.options = options
        self.status = status


    def __repr__(self):
        tz = pytz.timezone('America/Chicago')
        ts = datetime.fromtimestamp(self.timestamp, tz).strftime('%Y-%m-%d %H:%M:%S')
        return "<PushItem(id='%d', task='%s', options='%s', username='%s', timestamp='%s', status='%d')>" % (
                     self.id, self.task, self.options, self.username, ts, self.status)


    