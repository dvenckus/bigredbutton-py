#
# brbqueue.py
#
from app.bigredbutton import app, engine, dbsession
from models.taskitem import TaskItem
import subprocess
#from os import sys, path, devnull
import os

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
        qm_path = os.path.abspath(os.path.dirname(__file__))
        # run as a background process
        #output = open('/var/log/bigredbutton/bigredbutton.log', 'a')
        devnull = open(os.devnull, 'wb')
        subprocess.Popen(['nohup', qm_path + "/tools/queue_manager.py"],
                         stdout=devnull,
                         stderr=devnull,
                         preexec_fn=os.setpgrp)
        #subprocess.Popen( qm_path + "/tools/queue_manager.py &", shell=True)
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
