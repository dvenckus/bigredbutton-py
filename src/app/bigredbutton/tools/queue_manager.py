#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from os import sys, path, unlink, getpid
import datetime
import pytz
import logging


QM_LOG_PREFIX = "[BRB Queue Manager] "
qm_log = None


def main():
  '''
  runs when called as an external script by bigredbutton
  this is an independent script not integrated with flask app
  Only 1 instance of queue_manager should be running
  '''
  
  DATABASE_URI = constants.SQLALCHEMY_DATABASE_URI
  tz = pytz.timezone(constants.TIMEZONE)

  if not pid_begin():
   sys.exit("The queue_manager is already running.  My work is done here.")

  # manage the queue
  try:
    log_init(tz)

    # add 'echo=True' to turn on logging for create_engine
    engine = create_engine(DATABASE_URI)

    # create a Session
    Session = sessionmaker(bind=engine)
    session = Session()

    task = session.query(TaskItem).order_by(TaskItem.id).first()

    while task:
      logging.info("Task found.\n{}\n".format(str(task)))

      
      # execute task
      saltTask = SaltTask(task)
      result = saltTask.run()

      logging.info("Task found.\n{}".format(str(task)))
      logging.info("Task run result: " + str(result))

      # archive the task as completed
      taskHistoryItem = TaskHistoryItem(task.username, task.task, task.options, str(result))
      session.add(taskHistoryItem)

      # clean up after task run
      session.delete(task)
      session.commit()

      # get the next task
      task = session.query(TaskItem).order_by(TaskItem.id).first()
      

  except NoResultFound as e:
    ignoreIt = True

  except Exception as e:
    #pid_end()
    msg = "Error: QueueManager main, {0!r}\nExiting...".format(e)
    logging.info(msg)
    sys.exit(msg)

  finally:
    pid_end()
    log_end(tz)
    


  # ----- end - main() -----


#
# usage statement
#
def usage():
  ''' Usage Statment '''
  print("queue_manager.py\n")

#
# log_init
#
def log_init(timezone):
  ''' '''
  logging.basicConfig(filename=constants.QM_LOGFILE, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
  logging.info("Begin QUEUE MANAGER")


#
# log_end
#
def log_end(timezone):
  ''' '''
  logging.info('QUEUE MANAGER... END')

#
# pid_begin
#
def pid_begin():
  ''' '''
  try:
    # check if the pid file already exists
    if path.isfile(constants.QM_PIDFILE):
      print("The queue_manager is already running.  My work is done here.")
      return False

    # create pidfile (as lock file -- we only want 1 queue_manager running at a time)
    pid = str(getpid())
    with open(constants.QM_PIDFILE,'w+') as f:
        f.write(pid + '\n')

    return True
  except Exception as e:
    print("Error: QueueManager, pid_begin()")

#
# pid_end
#
def pid_end():
  ''' '''
  try:
    unlink(constants.QM_PIDFILE)
  except Exception as e:
    ignoreIt = True


#
# call the main function
#
if __name__ == "__main__":
  #if __package__ is None:
  
  app_path = path.dirname(path.dirname(path.abspath(__file__)))
  src_dir = path.dirname(path.dirname(app_path))
  sys.path.append(app_path)
  sys.path.append(src_dir)

  import constants 

  brb_env_libs = constants.VIRTUAL_ENV + '/lib/python3.5/site-packages'
  sys.path.append(brb_env_libs)
  sys.path.append(constants.SALTLIBS)
  sys.path.append(constants.DEV_SALTLIBS)

  from salttask import SaltTask
  from models.meta import Base
  from models.taskitem import TaskItem
  from models.taskhistoryitem import TaskHistoryItem
    
  
  main()
