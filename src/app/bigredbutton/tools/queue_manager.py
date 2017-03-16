#!/usr/bin/env python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from os import sys, path, unlink, getpid
import datetime
import pytz

app_path = ''

def main():
  '''
  runs when called as an external script by bigredbutton
  this is an independent script not integrated with flask app
  Only 1 instance of queue_manager should be running
  '''

  DATABASE_NAME = app_path + '/database/brb.db'
  QM_PIDFILE = '/var/run/bigredbutton/brb_queue_manager.pid'
  QM_LOGFILE = '/var/log/bigredbutton/brb_queue_manager.log'
  tz = pytz.timezone('America/Chicago')


  # check if the pid file already exists
  if path.isfile(QM_PIDFILE):
    print("The queue_manager is already running.  My work is done here.")
    sys.exit()

  # create pidfile (as lock file -- we only want 1 queue_manager running at a time)
  pid = str(getpid())
  #file(QM_PIDFILE, 'w').write(pid)
  with open(QM_PIDFILE,'w+') as f:
      f.write(pid + '\n')

  # manage the queue
  try:
    qm_log = open('/var/log/bigredbutton/brb_queue_manager.log', 'a', 4)
    now = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    qm_log.write("[BRB Queue Manager] BEGIN [{}]\n".format(now))
    qm_log.write('[BRB Queue Manager] sys.path: ' + str(sys.path) + "\n")

    qm_log.write("[BRB Queue Manager] Retrieve tasks\n")

    # add 'echo=True' to turn on logging for create_engine
    engine = create_engine('sqlite:///' + DATABASE_NAME)

    # create a Session
    Session = sessionmaker(bind=engine)
    session = Session()

    task = session.query(TaskItem).order_by(TaskItem.id).first()

    while task:
      qm_log.write("[BRB Queue Manager] Task found.\n" + str(task) + "\n")
      #print("Task found. " + str(task))

      # execute task
      result = SaltTask.run(task)
      #print("Task result. " + str(result))
      qm_log.write("[BRB Queue Manager] Task run result: " + str(result) + "\n")

      # clean up after task run
      session.delete(task)
      session.commit()

      # get the next task
      task = session.query(TaskItem).order_by(TaskItem.id).first()

  except NoResultFound as e:
    ignoreThis = 1

  except Exception as e:
    unlink(QM_PIDFILE)
    msg = "Error: {0!r}\nExiting...\n".format(e)
    qm_log.write(msg)
    sys.exit(msg)

  finally:
    try:
      unlink(QM_PIDFILE)
    except Exception as e:
      ignoreIt = True
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    qm_log.write("[BRB Queue Manager] END [{}]\n".format(now))


  # ----- end - main() -----


#
# usage statement
#
def usage():
  ''' Usage Statment '''
  print("queue_manager.py\n")


#
# call the main function
#
if __name__ == "__main__":
  if __package__ is None:
    app_path = path.dirname(path.dirname(path.abspath(__file__)))
    src_dir = path.dirname(path.dirname(app_path))
    sys.path.append(app_path)
    sys.path.append(src_dir + "/brb_env/lib/python3.5/site-packages")
    from models.meta import Base
    from models.user import User
    from models.taskitem import TaskItem
    from tools.salttask import SaltTask

  main()
