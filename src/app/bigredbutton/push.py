#
# push.py
#
from app.bigredbutton import app, engine, metadata
from tools.salttask import SaltTask
from models.pushitem import PushItem
import subprocess
from os import sys, path

class Push(object):

  @staticmethod
  def do(username, data):
    ''' PRODUCTION tasks -- do a BRB task immediately '''
    print('push (data): ', str(data))
    # there should only be 1 record
    subdomain = 'forum' if data['site'] == 'frm' else 'www2'
    pushitem = PushItem(username, subdomain, data['site'], data['task'], data['dbbackup'])
    return SaltTask.run(pushitem, 'push')
