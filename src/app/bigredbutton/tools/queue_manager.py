#!/usr/bin/env python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from os import sys, path, unlink, getpid
import datetime
import pytz


tz = pytz.timezone(config.TIMEZONE)
QM_PIDFILE = config.QM_PIDFILE
QM_LOGFILE = config.QM_LOGFILE
QM_LOG_PREFIX = "[BRB Queue Manager] "
qm_log = None


def main():
  '''
  runs when called as an external script by bigredbutton
  this is an independent script not integrated with flask app
  Only 1 instance of queue_manager should be running
  '''
  
  DATABASE_URI = config.SQLALCHEMY_DATABASE_URI

  if not pid_begin():
    sys.exit("The queue_manager is already running.  My work is done here.")

  # manage the queue
  try:
    log_init()

    # add 'echo=True' to turn on logging for create_engine
    engine = create_engine(DATABASE_URI)

    # create a Session
    Session = sessionmaker(bind=engine)
    session = Session()

    task = session.query(TaskItem).order_by(TaskItem.id).first()

    while task:
      log_msg("Task found.\n{}\n".format(str(task)))

      # execute task
      result = SaltTask.run(task)
      log_msg("Task found.\n{}".format(str(task)))
      log_msg("Task run result: " + str(result))

      # clean up after task run
      session.delete(task)
      session.commit()

      # get the next task
      task = session.query(TaskItem).order_by(TaskItem.id).first()

  except NoResultFound as e:
    ignoreIt = True

  except Exception as e:
    pid_end()
    msg = "Error: {0!r}\nExiting...".format(e)
    log_msg(msg)
    sys.exit(msg)

  finally:
    pid_end()
    log_end()
    


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
def log_init():
  ''' '''
  qm_log = open(QM_LOGFILE, 'a', 4)
  now = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
  log_msg("BEGIN [{}]".format(now))
  log_msg("sys.path: {}".format(str(sys.path)))
  log_msg("Retrieve tasks")

#
# log_msg
#
def log_msg(msg):
  ''' '''
  try:
    qm_log.write(QM_LOG_PREFIX + msg + "\n")
  except Exception:
    ignoreIt = True

#
# log_end
#
def log_end():
  ''' '''
  now = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
  log_msg("END [{}]".format(now))

#
# pid_begin
#
def pid_begin():
  ''' '''
  # check if the pid file already exists
  if path.isfile(QM_PIDFILE):
    print("The queue_manager is already running.  My work is done here.")
    return False

  # create pidfile (as lock file -- we only want 1 queue_manager running at a time)
  pid = str(getpid())
  with open(QM_PIDFILE,'w+') as f:
      f.write(pid + '\n')

  return True

#
# pid_end
#
def pid_end():
  ''' '''
  try:
    unlink(QM_PIDFILE)
  except Exception as e:
    ignoreIt = True


#
# call the main function
#
if __name__ == "__main__":
  if __package__ is None:
    app_path = path.dirname(path.dirname(path.abspath(__file__)))
    src_dir = path.dirname(path.dirname(app_path))
    sys.path.append(app_path)
    sys.path.append(src_dir)
    
    from models.meta import Base
    from models.user import User
    from models.taskitem import TaskItem
    from salttask import SaltTask

    import config 
    brb_env_libs = config.BRB_ENV + '/lib/python3.5/site-packages'
    sys.path.append(brb_env_libs)
    

  main()
