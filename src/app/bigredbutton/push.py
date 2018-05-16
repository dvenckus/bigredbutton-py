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
    ''' do a BRB task immediately '''

    print('push (data): ', str(data))
    pushitem = None

    if data['task'] in ['merge', 'versionup']:
      pushitem = PushItem(username, data['task'], options=data)
    else:
      options = {
        'subdomain': SubdomainsList.getSubdomain(data['site'], '', 'prod'),
        'site': data['site'],
        'dbbackup': data['dbbackup']
      }
      pushitem = PushItem(username, data['task'], options=options)

    saltTask = SaltTask(pushitem, 'push')

    return saltTask.run()
