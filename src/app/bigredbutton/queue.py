#
# queue.py
#
from app.bigredbutton import app, db
from models.taskitem import TaskItem
import subprocess
#from os import sys, path, devnull
import os

class Queue(object):

  @staticmethod
  def get(id=0, status=0):
    '''  '''
    tasks = None

    if id > 0:
      tasks = db.session.query(TaskItem).filter_by(id=id, status=status).first()
    else:
      tasks = db.session.query(TaskItem).filter_by(status=status).all()

    return tasks


  @staticmethod
  def add(username, data):
    ''' add groups of tasks to queue '''
    print 'queue_add (data): ', str(data)
    doCommit = False
    for item in data:
      task = TaskItem(username, item['subdomain'], item['site'], item['task'], item['dbbackup'])
      db.session.add(task)
      doCommit = True

    if doCommit:
      db.session.commit()
      try:
        # start the queue_manager
        qm_path = os.path.abspath(os.path.dirname(__file__))
        # run as a background process
        devnull = open(os.devnull, 'wb') # use this in python < 3.3; python >= 3.3 has subprocess.DEVNULL
        subprocess.Popen(['nohup', qm_path + "/tools/queue_manager.py"], stdout=devnull, stderr=devnull)
        #subprocess.Popen( qm_path + "/tools/queue_manager.py &", shell=True)
        return True
      except socket.error, e:
        # this is a socket error -- ignore
        # we don't care if the socket with queue_manager.py breaks, it's a standalone daemon process
        ignoreThis = 1
      except IOError, e:
        # this is an IO EPIPE error -- ignore
        # we don't care if the socket with queue_manager.py breaks, it's a standalone daemon process
        ignoreThis = 2


    return False



  @staticmethod
  def cancel(id):
    ''' delete task from f '''
    task = Queue.get(id)
    if task:
      db.session.delete(task)
      db.session.commit()
      return True

    return False
