#
# push.py
#
from app.bigredbutton import app, db
from tools.salttask import SaltTask
from app.bigredbutton.models.pushitem import PushItem
from app.bigredbutton.sites import SitesList
import subprocess
from os import sys, path

class Push(object):

  @staticmethod
  def do(username, data):
    ''' PRODUCTION tasks -- do a BRB task immediately '''
    print('push (data): ', str(data))
    # there should only be 1 record
    subdomain = SitesList.getProductionSubdomain(data['site'])
    pushitem = PushItem(username, subdomain, data['site'], data['task'], data['dbbackup'])
    return SaltTask.run(pushitem, 'push')
