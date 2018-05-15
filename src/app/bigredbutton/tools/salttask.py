#
# salttask.py
#
# called by queue_manager
from os import path, sys, linesep
import datetime
import pytz
import time
import redis
import subprocess
import smtplib
from email.mime.text import MIMEText
from models.meta import Base
from tasks import TasksList
import constants


# connect to redis server for message stream handling

class SaltTask(object):

  _redis = redis.StrictRedis(unix_socket_path=constants.REDIS_SOCKET_PATH)
  channel = constants.EVENT_STREAM_CHANNEL
  tz = pytz.timezone(constants.TIMEZONE)
  scripts_dir = constants.SCRIPTS_DIR + '/'

  logfile = None
  logname = constants.TASK_LOGFILE
  # .format(datetime.date.today().strftime('%Y%m%d'))

  doSiteSync = scripts_dir + 'brb_site_sync.py'
  doSiteDeploy = scripts_dir + 'brb_site_deploy.py'
  doCacheClear = scripts_dir + 'brb_site_cache_clear.py'
  doVarnishClear = scripts_dir + 'brb_varnish_clear.py'
  doRollback = scripts_dir + 'brb_site_rollback.py'
  doBulkLoad = scripts_dir + 'brb_bulk_load.py'
  doMerge = scripts_dir + 'brb_merge.py'
  doVersionUpdate = scripts_dir + 'brb_version_update.py'

  #Email Settings
  emailEnabled = constants.EMAIL_ENABLED
  emailFrom = constants.EMAIL_FROM
  emailTo = constants.EMAIL_TO


  taskItem = None
  taskOptions = None
  taskDesc = ''
  taskMode = ''


  def __init__(self, taskItem, mode='task'):
    ''' init a TaskItem '''

    self.taskMode = mode

    if self.taskMode == 'task':
      # TaskItem model is linked to its DB table
      from models.taskitem import TaskItem
    elif self.taskMode == 'push':
      # PushItem model does not have a DB relationship
      from models.pushitem import PushItem

    self.taskItem = taskItem
    self.taskOptions = taskItem.parseOptions()
    self.taskDesc = "({}) {} {} {} {}".format(
                  taskItem.username, 
                  taskOptions['subdomain'], 
                  taskOptions['site'], 
                  taskItem.task, 
                  taskOptions['backup_param'])
    self.taskOptions['backup_param'] = 'backup' if self.taskOptions.get('dbbackup', False) == True else ''



  def run(self):
    ''' runs the tasks requested through BRB '''
    # local vars
    output = ''
    errormsg = ''

    ### run the task
    try:
      self.logStart(taskDesc)
      self.pushMessage('BEGIN TASK ' + taskDesc)

      self.log("SaltTask::do")
      self.log(self.taskItem)
      self.log(self.taskOptions)
      output, errormsg = self.do()

      self.log(output)

      if len(errormsg):
        self.log('An Error occurred')
        self.log(errormsg)
        self.pushMessage('An Error occurred ' + str(errormsg))

      self.pushMessage("END TASK with {} {}".format('ERROR' if len(errormsg) else 'SUCCESS', self.taskDesc))
      self.logEnd(self.taskDesc)
      self.sendEmail(output, errormsg)

    except IOError as e:
      # this is an IO EPIPE error -- ignore
      #ignoreThis = 2
      print("[SaltTask] IOError: " + str(e) + "\n")
      SaltTask.log("[SaltTask] IOError: " + str(e))
    except Exception as e:
      print("[SaltTask] Exception: " + str(e) + "\n")
      SaltTask.log("[SaltTask] Exception: " + str(e))
      return output


  def pushMessage(self, msg):
    ''' push message to channel '''
    if msg == '': return
    ### publish message to alert channel
    #SaltTask.log("SaltTask::pushMessage()\n")
    dt = datetime.datetime.now(SaltTask.tz)
    now = dt.strftime('%Y-%m-%d %H:%M:%S')
    ts = int(dt.strftime("%s"))
    pub_msg = "[{0}] {1}".format(now, msg)
    self._redis.publish(SaltTask.channel, pub_msg)
    # set redis history expiration after 1 hour
    key = 'BRB_{}'.format(ts)
    self._redis.set(key, pub_msg)
    self._redis.expire(key, 3600)


  @staticmethod  
  def logStart(self, msg):
    '''
    marks the beginning of the task in the log
    using plain file log instead of python logging lib due to multiline formatting restrictions
    '''
    ### setup logging
    #print("[SaltTask] SaltTask::logStart()\n")
    now = datetime.datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S')
    #print("[SaltTask] Open Log: " + SaltTask.logname + "\n")
    self.logfile = open(SaltTask.logname, 'a', 4)
    self.logfile.write("\n\n--------- BEGIN Task [{}] ---------\n".format(now))
    self.logfile.write('Task:  ' + msg + "\n")
    self.logfile.write("---------------------------------------------------\n")


  def logEnd(self, msg):
    ''' marks the beginning of the task in the log '''
    ### setup logging
    now = datetime.datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S')
    self.logfile.write("--------- END Task [{}]---------\n".format(now))
    self.logfile.write('Task:  ' + msg + "\n")
    self.logfile.write("---------------------------------------------------\n")




  def log(self, msg):
    ''' log a message '''
    #print('[SaltTask] ' + str(msg) + "\n")
    self.logfile.write(str(msg) + "\n")


  def sendEmail(self, taskOutput, errormsg):
    ''' sends an email to dev team '''

    if self.emailEnabled == False:
      # email off, don't send
      return

    # Create a text/plain message
    msg = MIMEText(taskOutput)
    msg['Subject'] = "BigRedButton Task Completed{0}: {1}".format(' (ERRORS)' if len(errormsg) else '', self.taskDesc)
    msg['From'] = self.emailFrom
    msg['To'] = self.emailTo

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    #SaltTask.log("SaltTask::sendEmail()\n")
    s = smtplib.SMTP('localhost')
    s.sendmail(self.emailFrom, [self.emailTo], msg.as_string())
    s.quit()



  def do(self):
    ''' call the salt command '''

    # get the official taskslist so we know what to do for the selected task
    tasksList = TasksList.getList()
    saltcmd = []
    output = ''
    errormsg = ''


    try:
      tasksList[self.taskItem.task]
    except NameError as e:
      errormsg = "Error:  task not defined\n"
      return errormsg


    if 'sync' == tasksList[self.taskItem.task]['do']:

      if self.taskItem.site == 'vf':
        saltcmd = [
          SaltTask.doBulkLoad,
          'tgt=' + self.taskItem.subdomain,
          'mode=sync'
        ]
      else:
        #print("SaltTask: In DO, tasksList sync " + str(self.taskItem) )
        saltcmd = [
          SaltTask.doSiteSync,
          'tgt=' + self.taskOptions['subdomain'],
          'site=' + self.taskOptions['site'],
          'mode=all'
        ]

      backup = self.taskOptions.get('backup_param', '')
      if backup != '': saltcmd.append(backup)  

    elif 'deploy' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        SaltTask.doSiteDeploy,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site'],
      ]
      backup = self.taskOptions.get('backup_param', '')
      if backup != '': saltcmd.append(backup)  

    elif 'cache' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        SaltTask.doCacheClear,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site']
      ]

    elif 'varnish' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        SaltTask.doVarnishClear,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site']
      ]

    elif 'rb' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        SaltTask.doRollback,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site']
      ]

    elif 'unrb' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        SaltTask.doRollback,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site'],
        'undo'
      ]

    elif 'merge' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        SaltTask.doMerge,
        'repo=' + self.taskOptions['mergeRepo'],
        'merge-to=' + self.taskOptions['mergeTo']
      ]
      if self.taskOptions['mergeTest']: saltcmd.append('test')

    elif 'versionup' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        SaltTask.doVersionUpdate,
        'repo=' + self.taskOptions['versionRepo']
      ]
      if self.taskOptions['versionIncrMajor']: 
        saltcmd.append('major')
      elif self.taskOptions['versionIncrMinor']: 
        saltcmd.append('minor')
      if self.taskOptions['versionTest']: saltcmd.append('test')
    else:
      saltcmd = []


    if saltcmd:
      # prepend 'sudo' to the saltcmd
      saltcmd_str = ''

      try:
        saltcmd[:0] = ['sudo']
        saltcmd_str = ', '.join(saltcmd)
        SaltTask.log("saltcmd: " + saltcmd_str)
        output = subprocess.check_output(saltcmd)
      except subprocess.CalledProcessError as e:
        errormsg = saltcmd_str  + "\nError: " + str(e)
      except Exception as e:
        output = saltcmd_str + "\nError: ", str(e)
        errormsg = str(e)

    else:
      output = errormsg = "Task not found ({})".format(tasksList[self.taskItem.task])

    #print('SaltTask End of Do')
    return (output, errormsg)
