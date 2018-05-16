#
# push.py
#
from app.bigredbutton import app, db
from tools.salttask import SaltTask
from subdomains import SubdomainsList
from models.meta import Base
from models.pushitem import PushItem
from models.taskhistoryitem import TaskHistoryItem
import subprocess
from os import sys, path



class Push(object):

  @staticmethod
  def do(username, data):
    ''' do a BRB task immediately '''

    print('push (data): ', str(data))
    pushitem = None
    options = data

    if data['task'] in ['merge', 'versionup']:
      pushitem = PushItem(username, data['task'], options=options)
    else:
      options = {
        'subdomain': SubdomainsList.getSubdomain(data['site'], '', 'prod'),
        'site': data['site'],
        'dbbackup': data['dbbackup']
      }
      pushitem = PushItem(username, data['task'], options=options)

    saltTask = SaltTask(pushitem, 'push')

    result = saltTask.run()

    # archive the task as completed
    taskHistoryItem = TaskHistoryItem(username, data['task'], options, str(result))
    db.session.add(taskHistoryItem)
    db.session.commit()

    return result
