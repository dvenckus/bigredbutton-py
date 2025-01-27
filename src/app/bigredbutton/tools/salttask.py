#
# salttask.py
#
# called by queue_manager
#
import subprocess
import constants
from tasks import TasksList
from pushlog import PushLog
# import importlib
from models.taskitem import TaskItem
from models.pushitem import PushItem
# import socket

# connect to redis server for message stream handling

class SaltTask(object):

  # scripts_dir = constants.SCRIPTS_DIR + '/'

  doSiteSync = constants.SCRIPT_SITE_SYNC
  doSiteDeploy = constants.SCRIPT_SITE_DEPLOY
  doCacheClear = constants.SCRIPT_CACHE_CLEAR
  doVarnishClear = constants.SCRIPT_VARNISH_CLEAR
  doRollback = constants.SCRIPT_ROLLBACK
  doBulkLoad = constants.SCRIPT_BULK_LOAD
  doMerge = constants.SCRIPT_MERGE_REPOS
  doMigrate = constants.SCRIPT_MIGRATE
  doVersionUpdate = constants.SCRIPT_VERSION_UPDATE
  doReleaseScript = constants.SCRIPT_RELEASE_SCRIPT
  doReleaseSite = constants.SCRIPT_SITE_RELEASE


  taskItem = None
  taskOptions = None
  taskDesc = ''
  taskMode = ''
  
  pushLog = None

  itemModule = None


  def __init__(self, taskItem):
    ''' init a TaskItem '''

    self.taskMode = 'push' if isinstance(taskItem, PushItem) else 'task'
    self.taskItem = taskItem
    self.taskOptions = taskItem.parseOptions()

    # define the string-version of the dbbackup setting
    self.taskOptions['backup_param'] = ''
    try:
      if self.taskOptions['dbbackup']:
        self.taskOptions['backup_param'] = 'backup'
    except KeyError:
      ignoreThis = True

    subdomain = ''
    try:
      subdomain = self.taskOptions['subdomain']
    except KeyError:
      ignoreThis = True

    site = ''
    try:
      site = self.taskOptions['site']
    except KeyError:
      ignoreThis = True

    relscript = ''
    try:
      relscript = self.taskOptions['script']
    except KeyError:
      ignoreThis = True


    self.taskDesc = "[{}] {} {} ({}) {}{}".format(
                  taskItem.task.upper(), 
                  subdomain, 
                  site, 
                  taskItem.username, 
                  self.taskOptions['backup_param'],
                  relscript)

    # Alert Channel messages are sent from here
    # Log Channel messages are sent from lower-level BRB salt scripts
    self.pushLog = PushLog(constants.CHANNEL_ALERT)
    


  def run(self):
    ''' runs the tasks requested through BRB '''
    # local vars
    output = ''
    errormsg = ''

    ### run the task
    try:
      # we're just pushing Alerts, not log messages
      self.pushLog.pushMessage('BEGIN TASK ' + self.taskDesc)

      output, errormsg = self.do()

      if len(errormsg):
        self.pushLog.send('An Error occurred ' + str(errormsg))

      # we're just pushing Alerts, not log messages
      self.pushLog.pushMessage("END TASK with {} {} [ID={}]".format('ERROR' if len(errormsg) else 'SUCCESS', self.taskDesc, self.taskItem.id))


    except IOError as e:
      # this is an IO EPIPE error -- ignore
      #ignoreThis = 2
      self.pushLog.send("[SaltTask] IOError: " + str(e))
    except Exception as e:
      self.pushLog.send("[SaltTask] Exception: " + str(e))
    
    return output



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


    if constants.TASK_SYNC == tasksList[self.taskItem.task]['do']:
      
      saltcmd = [
        self.doSiteSync,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site'],
        'mode=all',
        'username=' + self.taskItem.username
      ]

      backup = self.taskOptions.get('backup_param', '')
      if backup != '': saltcmd.append(backup)  


    elif constants.TASK_MSYNC == tasksList[self.taskItem.task]['do']:
      # migration sync

      if self.taskOptions['site'] == 'vc':
        saltcmd = [
          self.doBulkLoad,
          'tgt=' + self.taskOptions['subdomain'],
          'mode=sync',
          'sync_mode=db',
          'dbkey=migrate',
          'username=' + self.taskItem.username
        ]
      else:
        saltcmd = [
          self.doSiteSync,
          'tgt=' + self.taskOptions['subdomain'],
          'site=' + self.taskOptions['site'],
          'mode=db',
          'dbkey=migrate',
          'username=' + self.taskItem.username
        ]

      backup = self.taskOptions.get('backup_param', '')
      if backup != '': saltcmd.append(backup)  

    elif constants.TASK_MIGRATE == tasksList[self.taskItem.task]['do']:
      # migration sync

      if self.taskOptions['subdomain'] in ['eve8']:
        saltcmd = [
          self.doMigrate,
          'tgt=' + self.taskOptions['subdomain'],
          'username=' + self.taskItem.username
        ]
      else:
        saltcmd = []

    elif constants.TASK_DEPLOY == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doSiteDeploy,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site'],
        'username=' + self.taskItem.username
      ]
      backup = self.taskOptions.get('backup_param', '')
      if backup: saltcmd.append(backup)  

      if self.taskOptions['site'] == 'vc':
        saltcmd.append('dbreset')  

    elif constants.TASK_CACHE == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doCacheClear,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site'],
        'username=' + self.taskItem.username
      ]

    elif constants.TASK_VARNISH == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doVarnishClear,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site'],
        'username=' + self.taskItem.username
      ]

    elif tasksList[self.taskItem.task]['do'] in [ constants.TASK_ROLLBACK, constants.TASK_ROLLBACK_UNDO ]:
      saltcmd = [
        self.doRollback,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site'],
        'username=' + self.taskItem.username
      ]
      if constants.TASK_ROLLBACK_UNDO == tasksList[self.taskItem.task]['do']: saltcmd.append('undo')


    elif constants.TASK_MERGE == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doMerge,
        'repo=' + self.taskOptions['mergeRepo'],
        'merge-to=' + self.taskOptions['mergeTo'],
        'username=' + self.taskItem.username
      ]
      if self.taskOptions['mergeTest']: saltcmd.append('test')

    elif constants.TASK_VERSION_UPDATE == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doVersionUpdate,
        'repo=' + self.taskOptions['versionRepo'],
        'username=' + self.taskItem.username
      ]
      if self.taskOptions['versionIncrMajor']: 
        saltcmd.append('major')
      elif self.taskOptions['versionIncrMinor']: 
        saltcmd.append('minor')
      if self.taskOptions['versionTest']: saltcmd.append('test')

    elif constants.TASK_RELEASE_SITE == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doReleaseSite,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site'],
        'username=' + self.taskItem.username
      ]

    elif constants.TASK_RELEASE_SCRIPT == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doReleaseScript,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site'],
        'script=' + self.taskOptions['script'],
        'username=' + self.taskItem.username
      ]

    else:
      saltcmd = []


    if saltcmd:
      # prepend 'sudo' to the saltcmd
      saltcmd_str = ''

      try:
        # this is the salt master, issue commandsd to subprocess
        saltcmd[:0] = ['/usr/bin/sudo']
        saltcmd_str = ', '.join(saltcmd)
        self.pushLog.send("saltcmd: " + saltcmd_str)
        output = subprocess.check_output(saltcmd)
      except subprocess.CalledProcessError as e:
        errormsg = saltcmd_str  + "\nError [SaltTask::do()]: " + str(e)
      except Exception as e:
        output = saltcmd_str + "\nError [SaltTask::do()]: ", str(e)
        errormsg = str(e)

    else:
      output = errormsg = "Task not found ({})".format(tasksList[self.taskItem.task])

    return (output, errormsg)
