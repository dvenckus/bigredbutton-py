#
# brbqueue.py
#
from app.bigredbutton import app, db
from models.taskitem import TaskItem
from app.bigredbutton.subdomains import SubdomainsList
from subprocess import Popen
from sqlalchemy import exc
import os
#import sys


class BrbQueue(object):

  @staticmethod
  def get(id=0, status=0):
    '''  '''
    tasks = None
    try:
      if int(id) > 0:
        tasks = db.session.query(TaskItem).filter_by(id=id, status=status).first()
      else:
        tasks = db.session.query(TaskItem).filter_by(status=status).all()
    except exc.SQLAlchemyError as e:
      print("Error: " + str(e) + "\n")

    return tasks


  @staticmethod
  def add(username, data):
    ''' add groups of tasks to queue '''

    print('queue_add (data): ', str(data))
    doCommit = False

    try:
      for item in data:
        # convert subdomain to forum subdomain if appropriate
        sd = SubdomainsList.getSubdomain(item['site'], item['subdomain'], 'pre-prod')
        task = TaskItem(username, sd, item['site'], item['task'], item['dbbackup'])
        db.session.add(task)
        doCommit = True

      if doCommit:
        db.session.commit()
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
      print("Error: " + str(e) + "\n")
    except exc.SQLAlchemyError as e:
      print("Error: " + str(e) + "\n")

    return False



  @staticmethod
  def cancel(id):
    ''' delete task '''
    try:
      task = BrbQueue.get(id)
      if task:
        db.session.delete(task)
        db.session.commit()
        return True
    except exc.SQLAlchemyError as e:
      print("Error: " + str(e) + "\n")

    return False
