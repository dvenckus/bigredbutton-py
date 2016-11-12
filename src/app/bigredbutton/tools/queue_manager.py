#!/usr/bin/env python
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import sys, path, unlink, getpid

app_path = ''

def main():
  '''
  runs when called as an external script by bigredbutton
  this is an independent script not integrated with flask app
  Only 1 instance of queue_manager should be running
  '''

  DATABASE_NAME = app_path + '/database/brb.db'
  PIDFILE = '/tmp/brb_queue_manager.pid'


  # check if the pid file already exists
  if path.isfile(PIDFILE):
    print "The queue_manager is already running.  My work is done here."
    sys.exit()

  # create pidfile (as lock file -- we only want 1 queue_manager running at a time)
  pid = str(getpid())
  file(PIDFILE, 'w').write(pid)

  # manage the queue
  try:
    # add 'echo=True' to turn on logging for create_engine
    engine = create_engine('sqlite:///' + DATABASE_NAME)

    # create a Session
    Session = sessionmaker(bind=engine)
    session = Session()

    task = session.query(TaskItem).order_by(TaskItem.id).first()

    while task:
      # execute task
      result = SaltTask.run(task)
      if result != False:
        # clean up after task run
        session.delete(task)
        session.commit()

      # get the next item in the queue
      task = session.query(TaskItem).order_by(TaskItem.id).first()



  except Exception,e:
    print "Error: ", e
    #unlink(PIDFILE)
    sys.exit('Exiting...\n')

  finally:
    unlink(PIDFILE)
    print "Done!\n"


  # ----- end - main() -----


#
# usage statement
#
def usage():
  ''' Usage Statment '''
  print "queue_manager.py\n"


#
# call the main function
#
if __name__ == "__main__":
  if __package__ is None:
    app_path = path.dirname(path.dirname(path.abspath(__file__)))
    sys.path.append(app_path)
    from models.meta import Base
    from models.user import User
    from models.taskitem import TaskItem
    from tools.salttask import SaltTask

  main()
