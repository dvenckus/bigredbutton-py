#
# salttask.py
#
# called by queue_manager

import datetime
import time
#from passlib.hash import sha256_crypt
#from gevent import monkey; monkey.patch_all()
import redis
from os import path, sys
import subprocess
import logging
import smtplib
from email.mime.text import MIMEText

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from models.meta import Base
from tasks import TasksList



# connect to redis server for message stream handling

class SaltTask(object):

  red = redis.StrictRedis()
  channel = 'alerts'

  logname = '/var/log/bigredbutton/bigredbutton.%s.log' % (datetime.date.today().strftime('%Y%m%d'))

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

    if mode == 'task':
      # TaskItem model is linked to its DB table
      from models.taskitem import TaskItem
    elif mode == 'push':
      # PushItem model does not have a DB relationship
      from models.pushitem import PushItem
    else:
      return False


    backup = 'backup' if taskitem.dbbackup == True else ''
    taskDesc = '(%s) %s %s %s %s' % (taskitem.username, taskitem.subdomain, taskitem.site, taskitem.task, backup)
    errormsg = ''

    ### run the task
    try:
      SaltTask.pushMessage('Task Beginning ' + taskDesc)
      SaltTask.logStart(taskDesc)

      output, errormsg = SaltTask.do(taskitem)

      logging.info(output)
      if len(errormsg):
        SaltTask.pushMessage('An Error occurred ' + errormsg)


      SaltTask.pushMessage('Task Ended in %s %s' % ('ERROR' if len(errormsg) else 'SUCCESS', taskDesc))
      SaltTask.logEnd(taskDesc)
      SaltTask.sendEmail(taskDesc, output, errormsg)
    except IOError as e:
      # this is an IO EPIPE error -- ignore
      ignoreThis = 2
    except Exception as e:
      ignoreThis = 3

    return output


  @staticmethod
  def pushMessage(msg):
    ''' push message to channel '''
    if msg == '': return

    ### publish message to alert channel
    now = datetime.datetime.now().replace(microsecond=0).time()
    SaltTask.red.publish(SaltTask.channel.decode('utf-8'), u'[%s] %s' % (now.isoformat(), msg))


  @staticmethod
  def logStart(msg):
    ''' marks the beginning of the task in the log '''
    ### setup logging
    now = datetime.datetime.now().replace(microsecond=0).time()
    logging.basicConfig(filename=SaltTask.logname,level=logging.INFO)

    logging.info("\n\n\n\n----- BEGIN Big Red Button [%s] %s -----\n" % (now.isoformat(), msg))

  @staticmethod
  def logEnd(msg):
    ''' marks the beginning of the task in the log '''
    ### setup logging
    now = datetime.datetime.now().replace(microsecond=0).time()
    logging.info("\n\n----- END Big Red Button [%s] %s -----\n" % (now.isoformat(), msg))


  @staticmethod
  def sendEmail(taskDesc, taskOutput, errormsg):
    ''' sends an email to dev team '''

    if SaltTask.emailEnabled == False:
      # email off, don't send
      return

    # Create a text/plain message
    msg = MIMEText(taskOutput)
    msg['Subject'] = 'BigRedButton Task Completed%s: %s' % (' (ERRORS)' if len(errormsg) else '', taskDesc)
    msg['From'] = SaltTask.emailFrom
    msg['To'] = SaltTask.emailTo

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(SaltTask.emailFrom, [SaltTask.emailTo], msg.as_string())
    s.quit()


  @staticmethod
  def do(taskitem):
    ''' call the salt command '''

    # get the official taskslist so we know what to do for the selected task
    tasksList = TasksList.get()
    saltcmd = ''
    saltscript = ''
    output = ''
    errormsg = ''

    try:
      tasksList[taskitem.task]
    except NameError as e:
      return "Error:  task not defined"

    if 'sync' == tasksList[taskitem.task]['do']:
      if taskitem.site == 'frm':
        saltscript = SaltTask.doBulkLoad
        saltcmd = "%s tgt=%s mode=sync %s" % (saltscript, taskitem.subdomain + '-forum','backup' if taskitem.dbbackup == True else '')

      else:
        saltscript = SaltTask.doSiteSync
        saltcmd = "%s tgt=%s site=%s mode=all %s" % (saltscript, taskitem.subdomain, taskitem.site, 'backup' if taskitem.dbbackup == True else '')

    elif 'deploy' == tasksList[taskitem.task]['do']:
      saltscript = SaltTask.doSiteDeploy
      saltcmd = "%s tgt=%s site=%s %s" % (saltscript, taskitem.subdomain, taskitem.site, 'backup' if taskitem.dbbackup == True else '')

    elif 'cache' == tasksList[taskitem.task]['do']:
      saltscript = SaltTask.doCacheClear
      saltcmd = "%s tgt=%s site=%s" % (saltscript, taskitem.subdomain, taskitem.site)

    elif 'varnish' == tasksList[taskitem.task]['do']:
      saltscript = SaltTask.doVarnishClear
      saltcmd = "%s tgt=%s site=%s" % (saltscript, taskitem.subdomain, taskitem.site)

    elif 'rb' == tasksList[taskitem.task]['do']:
      saltscript = SaltTask.doRollback
      saltcmd = "%s tgt=%s site=%s" % (saltscript, taskitem.subdomain, taskitem.site)

    elif 'unrb' == tasksList[taskitem.task]['do']:
      saltscript = SaltTask.doRollback
      saltcmd = "%s tgt=%s site=%s undo" % (saltscript, taskitem.subdomain, taskitem.site)

    if not path.isfile(saltscript):
      time.sleep(20)
      output = errormsg = "Error: salt script, %s, not found" % (saltscript)
      return (output, errormsg)

    if saltcmd != '':
      try:
        p = subprocess.Popen([saltcmd], stdout=subprocess.PIPE)
        output, errormsg = p.communicate()
        output += saltcmd + "\n" + errormsg
      except Exception as e:
        output = saltcmd + "\nError: ", str(e)
        errormsg = str(e)

    else:
      output = errormsg = "Task not found (%s)" % tasksList[taskitem.task]

    return (output, errormsg)
