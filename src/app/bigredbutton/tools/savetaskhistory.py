#!/usr/local/python_virtualenv/bigredbutton/bin/python
# run this within the bigredbutton virtualenv

#
# Call this class while using the bigredbutton virtualenv
#
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import sys
import os
import getopt
import ast
from clint.textui import colored, puts
import json


def main(username='', task='', options='', result=''):
  ''' 
  logs BRB tasks to the Task History if they are run on the commandline
  returns a tuple:  True|False and message
  '''
  #pushLog = None
  e = None 

  try:

    SCRIPT_TITLE = 'SaveTaskHistory'
    VERSION_UPDATE_SCRIPT = constants.SCRIPTS_DIR + '/git_version_update.sh'

    username = ''
    task = ''
    options = ''
    result = ''

    try:
      opts, args = getopt.getopt(sys.argv[1:], "", ["username=", "task=", "options=", "result="])
    except getopt.GetoptError:
      print('Error (SaveTaskHistory):  missing arguments')
      #usage()
      sys.exit(2)

    for a in args:
      if "username=" in a:
        tmp = a.split('=')
        username = tmp[1]
      elif "task=" in a:
        tmp = a.split('=')
        task = tmp[1]
      elif "options=" in a:
        tmp = a.split('=')
        options = tmp[1]
      elif "result=" in a:
        tmp = a.split('=')
        s = str(tmp[1])
        result = s
    

    if not username or not task:
      print('Error (SaveTaskHistory):  missing arguments')
      #usage()
      sys.exit(2)

    # init the db engine
    engine = create_engine(constants.SQLALCHEMY_DATABASE_URI)

    # create the session
    Session = sessionmaker(bind=engine)
    session = Session()


    #msg = "[SaveTaskHistory] username: {}; task: {}; options: {}; \nresult: {}".format(username, task, options, result)
    #print(msg)

    # archive the task as completed
    taskHistoryItem = TaskHistoryItem(username=username, task=task, options=options, result=result)
    session.add(taskHistoryItem)
    session.commit()

    return True
  except exc.SQLAlchemyError as e: 
    print("Error (SaveTaskHistory): " + str(e))
    return False
  except Exception as e:
    print("Error (SaveTaskHistory): " + str(e))
    return False

 # print("Task History saved")



#
# call the main function
#
if __name__ == "__main__":
  #if __package__ is None:

  #app_path = path.dirname(path.dirname(path.abspath(__file__)))
  #src_dir = path.dirname(path.dirname(app_path))
  #sys.path.append(app_path)
  #sys.path.append(src_dir)
  bigredbutton_site_dir = os.getenv('BIGREDBUTTON_SITE_DIR', '/var/www/html/bigredbutton.veritashealth.com/src')
  if bigredbutton_site_dir != '':  
    sys.path.append(bigredbutton_site_dir)
    sys.path.append(bigredbutton_site_dir + '/app/bigredbutton')
  else:
    print("syspath: " + sys.path)

  import constants 
  

  brb_env_libs = constants.VIRTUAL_ENV + '/lib/python3.5/site-packages'
  sys.path.append(brb_env_libs)
  sys.path.append(constants.SALTLIBS)
  # sys.path.append(constants.DEV_SALTLIBS)
  # sys.path.append(constants.DEVLIBS)
  # sys.path.append(constants.DEVSCRIPTS)

  from models.taskhistoryitem import TaskHistoryItem
  #from pushlog import PushLog
    
  
  main()


