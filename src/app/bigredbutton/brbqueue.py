#
# brbqueue.py
#
from app.bigredbutton import app, engine, dbsession
from models.taskitem import TaskItem
from subprocess import Popen
import os
#import sys


class BrbQueue(object):

  @staticmethod
  def get(id=0, status=0):
    '''  '''
    tasks = None

    if int(id) > 0:
      tasks = dbsession.query(TaskItem).filter_by(id=id, status=status).first()
    else:
      tasks = dbsession.query(TaskItem).filter_by(status=status).all()

    return tasks


  @staticmethod
  def add(username, data):
    ''' add groups of tasks to queue '''
    print('queue_add (data): ', str(data))
    doCommit = False
    for item in data:
      task = TaskItem(username, item['subdomain'], item['site'], item['task'], item['dbbackup'])
      dbsession.add(task)
      doCommit = True

    if doCommit:
      dbsession.commit()
      try:
        # start the queue_manager
        qm_path = os.path.dirname(__file__)
        # run as a background process
        brb_log = open('/var/log/bigredbutton/brb-py.log', 'a', 4)
        error_log = open('/var/log/bigredbutton/brb-py.error.log', 'a', 4)
        #devnull = open(os.devnull, 'w')
        virt_env = name = os.environ.get('VIRTUAL_ENV')
        qm_path = os.path.dirname(virt_env) + '/app/bigredbutton/tools'
        queue_manager =  qm_path + '/queue_manager.py'
        python_bin = virt_env + '/bin/python'

        Popen(['nohup', python_bin, queue_manager, '&'], stdout=brb_log, stderr=error_log)
        return True
      except IOError as e:
        # this is an IO EPIPE error -- ignore
        # we don't care if the socket with queue_manager.py breaks, it's a standalone daemon process
        ignoreThis = 2

    return False



  @staticmethod
  def cancel(id):
    ''' delete task from f '''
    task = BrbQueue.get(id)
    if task:
      dbsession.delete(task)
      dbsession.commit()
      return True

    return False
