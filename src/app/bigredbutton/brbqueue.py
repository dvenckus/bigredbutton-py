#
# brbqueue.py
#
from app.bigredbutton import app, db
from models.taskitem import TaskItem
from app.bigredbutton.subdomains import SubdomainsList
import subprocess
from sqlalchemy import exc
import os
import json


class BrbQueue(object):

  @staticmethod
  def get(id=0):
    '''  '''
    tasks = None
    try:
      #app.logger.info("TaskItem id="+str(id))
      if int(id) > 0:
        tasks = db.session.query(TaskItem).filter_by(id=id).first()
      else:
        tasks = db.session.query(TaskItem).all()

    except exc.SQLAlchemyError as e:
      app.logger.error("BrbQueue::get()")
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error("BrbQueue::get()")
      app.logger.error(str(e))

    return tasks


  @staticmethod
  def get_task(site, subdomain, task):
    ''' 
    retrieve a task based on site, subdomain, task, if it exists in the queue
    '''
    task = None
    try:
      #app.logger.info("TaskItem id="+str(id))
      if not site or not subdomain or not task:
        return task

      task = db.session.query(TaskItem).filter_by(site=site, subdomain=subdomain, task=task).first()

    except exc.SQLAlchemyError as e:
      app.logger.error("BrbQueue::get()")
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error("BrbQueue::get()")
      app.logger.error(str(e))

    return task



  @staticmethod
  def add(username, data):
    ''' add groups of tasks to queue '''

    doCommit = False

    try:
      tasklist = data['tasks']
      if len(tasklist):
        for item in tasklist:
          # app.logger.info("BrbQueue::add(): item {}".format(item))

          if username == 'api_request' and BrbQueue.get_task(item['site'], item['subdomain'], item['task']):
            # task already exists in queue, do not add it again from salt reactor trigger
            continue
        

          subdomain = SubdomainsList.getSubdomain(item['site'], item['subdomain'], 'pre-prod')
          opt_backup = ''
          opt_relscript = ''
          
          # create a json-compatible string to pass to the TaskItem object
          # double braces in format() indicate use of a literal
          try:
            opt_backup = ', "dbbackup": {}'.format(item['dbbackup'])
          except KeyError:
            opt_backup = ''

          try:
            opt_relscript = ', "script": "{}"'.format(item['relscript'])
          except KeyError:
            opt_relscript = ''


          options = '{{ "subdomain": "{}", "site": "{}"{}{} }}'.format(subdomain, item['site'], opt_backup, opt_relscript)
                        
          # app.logger.info("BrbQueue::add(): options " + options)
          task = TaskItem(username, str(item['task']), options=options)
          db.session.add(task)

      # after for loop, commit all new items
      db.session.commit()
      return True
      
    except IOError as e:
      # this is an IO EPIPE error -- ignore
      # we don't care if the socket with queue_manager.py breaks, it's a standalone daemon process
      app.logger.error("BrbQueue::add(), IOError")
      app.logger.error(str(e))
    except exc.SQLAlchemyError as e:
      app.logger.error("BrbQueue::add(), SQLAlchemyError")
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error("BrbQueue::add() Exception")
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
      app.logger.error("BrbQueue::cancel()")
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error("BrbQueue::cancel()")
      app.logger.error(str(e))

    return False


  @staticmethod
  def runQueueManager(delay=0):
    ''' starts the queue_manager in the event there are any tasks to run '''
    try:
      # start the queue_manager
      # run as a background process
      log_file = app.config['LOG_FILE']

      brb_log = open(log_file, 'a', 4)
      #brb_virt_env = app.config['VIRTUAL_ENV']
      qm_path = os.path.dirname(__file__) + '/tools'
      queue_manager =  qm_path + '/queue_manager.py'
      #python_bin = brb_virt_env + '/bin/python'
      #subprocess.Popen(['whoami'], stdout=brb_log, stderr=brb_log)
      subprocess.call([queue_manager, '-d', str(delay), '&'], shell=True, stdout=brb_log, stderr=brb_log)

    except Exception as e:
      app.logger.error("BrbQueue::runQueueManager()")
      app.logger.error(str(e))
