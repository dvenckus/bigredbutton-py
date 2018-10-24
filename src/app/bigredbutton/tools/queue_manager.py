#!/usr/bin/env python3
# turn off output buffering
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from os import sys, path, unlink, getpid, environ
import datetime
import pytz
import re
import logging
import getopt
import time


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
  delay = 0

  if not pid_begin():
   sys.exit("The queue_manager is already running.  My work is done here.")


  try:
    opts, args = getopt.getopt(sys.argv[1:], "d:", ["delay="])
  except getopt.GetoptError:
    print('Error:  missing arguments')
    usage()
    sys.exit(2)

  # handle options/args either way
  for o, a in opts:
    if o in ("-d", "--delay"):
      delay = a

  for a in args:
    if "delay=" in a:
      tmp = a.split('=')
      delay = tmp[1]

  # delay for n seconds
  if int(delay) > 0:
    time.sleep(int(delay))

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
      saltTask = SaltTask(taskItem=task)
      output = saltTask.run()

      logging.info("Task found.\n{}".format(str(task)))
      logging.info("Task Options: " + str(task.options))
      logging.info("Task run output: " + str(output))

      # archive the task as completed

      # retrieve the final result from the full output
      result = Utils.parseTaskResult(output)

      taskHistoryItem = TaskHistoryItem(task.username, task.task, task.options, result, output)
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
    logging.info('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
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

  venv = constants.VIRTUAL_ENV
  if not venv:
    venv = environ.get('VIRTUAL_ENV')

  sys.path.append(constants.VIRTUAL_ENV_LIBS)
  sys.path.append(constants.SALTLIBS)
  # sys.path.append(constants.DEV_SALTLIBS)
  # sys.path.append(constants.DEVLIBS)
  # sys.path.append(constants.DEVSCRIPTS)

  from salttask import SaltTask
  from models.taskitem import TaskItem
  from models.taskhistoryitem import TaskHistoryItem
  from utils import Utils
    
  
  main()
