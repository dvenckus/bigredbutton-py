#
# salttask.py
#
# called by queue_manager
from os import path, sys, linesep
import datetime
import time
import redis
import subprocess
import smtplib
from email.mime.text import MIMEText
from models.meta import Base
from tasks import TasksList



# connect to redis server for message stream handling

class SaltTask(object):

  redis_ch = redis.StrictRedis()
  channel = 'alerts'

  logfile = None
  logname = '/var/log/bigredbutton/brb_tasks.log'   # .format(datetime.date.today().strftime('%Y%m%d'))

  doSiteSync = '/var/www/scripts/brb_site_sync.py'
  doSiteDeploy = '/var/www/scripts/brb_site_deploy.py'
  doCacheClear = '/var/www/scripts/brb_site_cache_clear.py'
  doVarnish = '/var/www/scripts/brb_varnish_clear.py'
  doRollback = '/var/www/scripts/brb_site_rollback.py'
  doBulkLoad = '/var/www/scripts/brb_bulk_load.py'

  #Email Settings
  emailEnabled = False
  emailFrom = 'bigredbutton@veritashealth.com'
  emailTo = 'dev@veritashealth.com'


  @staticmethod
  def run(taskitem, mode='task'):
    ''' runs the tasks requested through BRB '''


    output = ''

    if mode == 'task':
      # TaskItem model is linked to its DB table
      from models.taskitem import TaskItem
    elif mode == 'push':
      # PushItem model does not have a DB relationship
      from models.pushitem import PushItem
    else:
      return False


    backup = 'backup' if taskitem.dbbackup == True else ''
    taskDesc = "({}) {} {} {} {}".format(taskitem.username, taskitem.subdomain, taskitem.site, taskitem.task, backup)
    errormsg = ''

    ### run the task
    try:
      SaltTask.logStart(taskDesc)
      SaltTask.pushMessage('BEGIN TASK ' + taskDesc)


      SaltTask.log("SaltTask::do")
      SaltTask.log(taskitem)
      output, errormsg = SaltTask.do(taskitem, backup)

      SaltTask.log(output)

      if len(errormsg):
        SaltTask.log('An Error occurred')
        SaltTask.log(errormsg)
        SaltTask.pushMessage('An Error occurred ' + str(errormsg))


      SaltTask.pushMessage("END TASK with {} {}".format('ERROR' if len(errormsg) else 'SUCCESS', taskDesc))
      SaltTask.logEnd(taskDesc)
      SaltTask.sendEmail(taskDesc, output, errormsg)

    except IOError as e:
      # this is an IO EPIPE error -- ignore
      #ignoreThis = 2
      print("[SaltTask] IOError: " + str(e) + "\n")
      SaltTask.log("[SaltTask] IOError: " + str(e))
    except Exception as e:
      #ignoreThis = 3
      print("[SaltTask] Exception: " + str(e) + "\n")
      SaltTask.log("[SaltTask] Exception: " + str(e))

    return output


  @staticmethod
  def pushMessage(msg):
    ''' push message to channel '''
    if msg == '': return
    ### publish message to alert channel
    #SaltTask.log("SaltTask::pushMessage()\n")
    now = datetime.datetime.now().replace(microsecond=0).time()
    SaltTask.redis_ch.publish(SaltTask.channel, "[{0}] {1}".format(now.isoformat(), msg))


  @staticmethod
  def logStart(msg):
    '''
    marks the beginning of the task in the log
    using plain file log instead of python logging lib due to multiline formatting restrictions
    '''
    ### setup logging
    #print("[SaltTask] SaltTask::logStart()\n")
    now = datetime.datetime.now().replace(microsecond=0).time()
    #print("[SaltTask] Open Log: " + SaltTask.logname + "\n")
    SaltTask.logfile = open(SaltTask.logname, 'a', 4)
    SaltTask.logfile.write("\n\n--------- BEGIN Task [{}] ---------\n".format(now))
    SaltTask.logfile.write('Task:  ' + msg + "\n")
    SaltTask.logfile.write("-----------------------------------------\n")


  @staticmethod
  def logEnd(msg):
    ''' marks the beginning of the task in the log '''
    ### setup logging
    now = datetime.datetime.now().replace(microsecond=0).time()

    SaltTask.logfile.write("--------- END Task [{}]---------\n".format(now))
    SaltTask.logfile.write('Task:  ' + msg + "\n")
    SaltTask.logfile.write("-----------------------------------------\n")




  @staticmethod
  def log(msg):
    ''' log a message '''
    #print('[SaltTask] ' + str(msg) + "\n")
    SaltTask.logfile.write(str(msg) + "\n")


  @staticmethod
  def sendEmail(taskDesc, taskOutput, errormsg):
    ''' sends an email to dev team '''

    if SaltTask.emailEnabled == False:
      # email off, don't send
      return

    # Create a text/plain message
    msg = MIMEText(taskOutput)
    msg['Subject'] = "BigRedButton Task Completed{0}: {1}".format(' (ERRORS)' if len(errormsg) else '', taskDesc)
    msg['From'] = SaltTask.emailFrom
    msg['To'] = SaltTask.emailTo

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    #SaltTask.log("SaltTask::sendEmail()\n")
    s = smtplib.SMTP('localhost')
    s.sendmail(SaltTask.emailFrom, [SaltTask.emailTo], msg.as_string())
    s.quit()


  @staticmethod
  def do(taskitem, backup=''):
    ''' call the salt command '''

    # get the official taskslist so we know what to do for the selected task
    tasksList = TasksList.get()
    saltcmd = []
    output = ''
    errormsg = ''


    try:
      tasksList[taskitem.task]
    except NameError as e:
      errormsg = "Error:  task not defined\n"
      return errormsg


    if 'sync' == tasksList[taskitem.task]['do']:

      if taskitem.site == 'frm' or taskitem.site == 'vf':
        saltcmd = [
          SaltTask.doBulkLoad,
          'tgt=' + taskitem.subdomain + '-forum',
          'mode=sync',
          backup
        ]

      else:
        #print("SaltTask: In DO, tasksList sync " + str(taskitem) )
        saltcmd = [
          SaltTask.doSiteSync,
          'tgt=' + taskitem.subdomain,
          'site=' + taskitem.site,
          'mode=all',
          backup
        ]

    elif 'deploy' == tasksList[taskitem.task]['do']:
      saltcmd = [
        SaltTask.doSiteDeploy,
        'tgt=' + taskitem.subdomain,
        'site=' + taskitem.site,
        backup
      ]

    elif 'cache' == tasksList[taskitem.task]['do']:
      saltcmd = [
        SaltTask.doCacheClear,
        'tgt=' + taskitem.subdomain,
        'site=' + taskitem.site
      ]

    elif 'varnish' == tasksList[taskitem.task]['do']:
      saltcmd = [
        SaltTask.doVarnishClear,
        'tgt=' + taskitem.subdomain,
        'site=' + taskitem.site
      ]

    elif 'rb' == tasksList[taskitem.task]['do']:
      saltcmd = [
        SaltTask.doRollback,
        'tgt=' + taskitem.subdomain,
        'site=' + taskitem.site
      ]

    elif 'unrb' == tasksList[taskitem.task]['do']:
      saltcmd = [
        SaltTask.doRollback,
        'tgt=' + taskitem.subdomain,
        'site=' + taskitem.site,
        'undo'
      ]
    else:
      saltcmd = []


    if saltcmd:
      # prepend 'sudo' to the saltcmd
      saltcmd[:0] = ['sudo']
      saltcmd_str = ', '.join(saltcmd)

      try:
        SaltTask.log("saltcmd: " + saltcmd_str)
        output = subprocess.check_output(saltcmd)
      except subprocess.CalledProcessError as e:
        errormsg = saltcmd_str  + "\nError: " + e.output
      except Exception as e:
        output = saltcmd_str + "\nError: ", str(e)
        errormsg = str(e)

    else:
      output = errormsg = "Task not found ({})".format(tasksList[taskitem.task])

    #print('SaltTask End of Do')
    return (output, errormsg)
