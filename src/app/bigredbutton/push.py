#
# push.py
#
from app.bigredbutton import app, db
from tools.salttask import SaltTask
from subdomains import SubdomainsList
#from models.meta import Base
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
    options = ''

    if data['task'] == 'merge':
      options = '{{ "mergeRepo": "{}", "mergeTo": "{}", "mergeTest": {} }}'.format(
                      data['mergeRepo'],
                      data['mergeTo'],
                      data['mergeTest'] )
    elif data['task'] == 'versionup':
      options = '{{ "versionRepo": "{}", "versionIncrMajor": {}, "versionIncrMinor": {}, "versionTest": {} }}'.format(
                      data['versionRepo'],
                      data['versionIncrMajor'],
                      data['versionIncrMinor'],
                      data['versionTest'] )
    else:
      # create a json-compatible string to pass to the TaskItem object
      # double braces in format() indicate use of a literal
      options = '{{ "subdomain": "{}", "site": "{}", "dbbackup": {} }}'.format(
                      SubdomainsList.getSubdomain(data['site'], '', 'prod'),
                      data['site'],
                      data['dbbackup'] )


    pushitem = PushItem(username, data['task'], options=options)

    saltTask = SaltTask(pushitem)

    result = saltTask.run()

    # archive the task as completed
    taskHistoryItem = TaskHistoryItem(username, data['task'], options, str(result))
    db.session.add(taskHistoryItem)
    db.session.commit()

    return result
