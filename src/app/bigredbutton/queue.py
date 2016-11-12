#
# queue.py
#
from app.bigredbutton import app, db
from models.taskitem import TaskItem
import subprocess
from os import sys, path

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
      # start the queue_manager
      qm_path = path.abspath(path.dirname(__file__))
      pid = subprocess.Popen( qm_path + "/tools/queue_manager.py", shell=True).pid
      return True

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
