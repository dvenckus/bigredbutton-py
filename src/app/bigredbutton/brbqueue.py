#
# brbqueue.py
#
from app.bigredbutton import app, db
from models.taskitem import TaskItem
from app.bigredbutton.subdomains import SubdomainsList
from subprocess import Popen
from sqlalchemy import exc
import os


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
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error(str(e))

    return tasks


  @staticmethod
  def add(username, data):
    ''' add groups of tasks to queue '''

    print('queue_add (data): ', str(data))
    doCommit = False

    try:
      for item in data:
        # convert subdomain to forum subdomain if appropriate
        options = {
          'subdomain':  SubdomainsList.getSubdomain(item['site'], item['subdomain'], 'pre-prod'),
          'site': item.get('site'),
          'dbbackup': item.get('dbbackup')
        }
        task = TaskItem(username, item['task'], options=options)
        db.session.add(task)
        doCommit = True

      if doCommit:
        db.session.commit()
        # initiate the QueueManager to run the new task
        BrbQueue.runQueueManager()
        return True

    except IOError as e:
      # this is an IO EPIPE error -- ignore
      # we don't care if the socket with queue_manager.py breaks, it's a standalone daemon process
      app.logger.error(str(e))
    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error(str(e))

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
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error(str(e))

    return False


  @staticmethod
  def runQueueManager():
    ''' starts the queue_manager in the event there are any tasks to run '''
    try:
      # start the queue_manager
      # run as a background process
      log_file = app.config['LOG_FILE']

      brb_log = open(log_file, 'a', 4)
      brb_virt_env = app.config['VIRTUAL_ENV']
      qm_path = os.path.dirname(__file__) + '/tools'
      queue_manager =  qm_path + '/queue_manager.py'
      python_bin = brb_virt_env + '/bin/python'

      Popen(['nohup', queue_manager, '&'], stdout=brb_log, stderr=brb_log)

    except Exception as e:
      app.logger.error("Exception in BrbQueue::runQueueManager()")
      app.logger.error(str(e))
