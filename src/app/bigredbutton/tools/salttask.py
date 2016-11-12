#
# salttask.py
#
# called by queue_manager

import datetime
from passlib.hash import sha256_crypt
from gevent import monkey; monkey.patch_all()
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
  doSiteSync = '/var/www/scripts/do_site_sync.py'
  doSiteDeploy = '/var/www/scripts/do_site_deploy.py'
  doCacheClear = '/var/www/scripts/do_cache_clear.py'
  doVarnish = '/var/www/scripts/do_varnish_clear.py'
  doRollback = '/var/www/scripts/do_rollback.py'

  emailFrom = 'bigredbutton@veritashealth.com'
  emailTo = 'dev@veritashealth.com'


  @staticmethod
  def run(taskitem, mode='task'):
    ''' runs the tasks requested through BRB '''

    if mode == 'task':
      from models.taskitem import TaskItem
    elif mode == 'push':
      from models.pushitem import PushItem
    else:
      return False


    backup = 'backup' if taskitem.dbbackup == True else ''
    taskDesc = '(%s) %s %s %s %s' % (taskitem.username, taskitem.subdomain, taskitem.site, taskitem.task, backup)

    ### run the task

    SaltTask.pushMessage('Beginning Task ' + taskDesc)
    SaltTask.logStart(taskDesc)

    output = SaltTask.do(taskitem)

    logging.info(output)
    SaltTask.sendEmail(taskDesc, output)

    SaltTask.pushMessage('Completed Task ' + taskDesc)
    SaltTask.logEnd(taskDesc)

    return output


  @staticmethod
  def pushMessage(msg):
    ''' push message to channel '''
    if msg == '': return

    ### publish message to alert channel
    now = datetime.datetime.now().replace(microsecond=0).time()
    SaltTask.red.publish(SaltTask.channel, u'[%s] %s' % (now.isoformat(), msg))


  @staticmethod
  def logStart(msg):
    ''' marks the beginning of the task in the log '''
    ### setup logging
    today = datetime.date.today().strftime('%Y%m%d')
    now = datetime.datetime.now().replace(microsecond=0).time()
    logname = 'bigredbutton.%s.log' % (today)
    logging.basicConfig(filename=logname,level=logging.INFO)

    logging.info("\n----- Big Red Button [%s] %s -----\n" % (now.isoformat(), msg))

  @staticmethod
  def sendEmail(taskDesc, taskOutput):
    ''' sends an email to dev team '''
    # Create a text/plain message
    msg = MIMEText(taskOutput)
    msg['Subject'] = 'BigRedButton Task Completed: ' + taskDesc
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

    try:
      tasksList[taskitem.task]
    except NameError:
      return "Error:  task not defined"

    if 'sync' == tasksList[taskitem.task]['do']:
      saltcmd = "%s tgt=%s site=%s mode=all %s" % (SaltTask.doSiteSync, taskitem.subdomain, taskitem.site, 'backup' if taskitem.dbbackup == True else '')

    elif 'deploy' == tasksList[taskitem.task]['do']:
      saltcmd = "%s tgt=%s site=%s %s" % (SaltTask.doSiteDeploy, taskitem.subdomain, taskitem.site, 'backup' if taskitem.dbbackup == True else '')

    elif 'cache' == tasksList[taskitem.task]['do']:
      saltcmd = "%s tgt=%s site=%s" % (SaltTask.doCacheClear, taskitem.subdomain, taskitem.site)

    elif 'varnish' == tasksList[taskitem.task]['do']:
      saltcmd = "%s tgt=%s site=%s" % (SaltTask.doVarnishClear, taskitem.subdomain, taskitem.site)

    elif 'rb' == tasksList[taskitem.task]['do']:
      saltcmd = "%s tgt=%s site=%s" % (SaltTask.doRollback, taskitem.subdomain, taskitem.site)

    elif 'unrb' == tasksList[taskitem.task]['do']:
      saltcmd = "%s tgt=%s site=%s undo" % (SaltTask.doRollback, taskitem.subdomain, taskitem.site)

    if saltcmd != '':
      print saltcmd
      p = subprocess.Popen([saltcmd], stdout=subprocess.PIPE)
      output, error = p.communicate()
      output += "\n" + error
    else:
      output = "Task not found (%s)" % tasksList[taskitem.task]

    return output
