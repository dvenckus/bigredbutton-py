#
# push.py
#
from app.bigredbutton import app, db
from tools.salttask import SaltTask
from app.bigredbutton.models.pushitem import PushItem
from app.bigredbutton.subdomains import SubdomainsList
import subprocess
from os import sys, path

class Push(object):

  @staticmethod
  def do(username, data):
    ''' PRODUCTION tasks -- do a BRB task immediately '''
    print('push (data): ', str(data))
    # there should only be 1 record
    subdomain = SubdomainsList.getSubdomain(data['site'], 'prod')
    pushitem = PushItem(username, subdomain, data['site'], data['task'], data['dbbackup'])
    return SaltTask.run(pushitem, 'push')
