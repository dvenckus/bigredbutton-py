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
  doVersionUpdate = constants.SCRIPT_VERSION_UPDATE


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

    try:
      self.taskOptions['backup_param'] = 'backup' if self.taskOptions['dbbackup']  == True else ''
    except KeyError:
      self.taskOptions['backup_param'] = ''

    subdomain = ''
    try:
      subdomain = self.taskOptions['subdomain']
    except KeyError:
      subdomain = ''

    site = ''
    try:
      site = self.taskOptions['site']
    except KeyError:
      site = ''

    self.taskDesc = "[{}] {} {} ({}) {}".format(
                  taskItem.task.upper(), 
                  subdomain, 
                  site, 
                  taskItem.username, 
                  self.taskOptions['backup_param'] )

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

      # No need to do this as its handled directly by the saltscripts now
      #self.pushLog.send(output)

      if len(errormsg):
        self.pushLog.send('An Error occurred ' + str(errormsg))

      # we're just pushing Alerts, not log messages
      self.pushLog.pushMessage("END TASK with {} {}".format('ERROR' if len(errormsg) else 'SUCCESS', self.taskDesc))


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


    if 'sync' == tasksList[self.taskItem.task]['do']:

      if self.taskOptions['site'] == 'vf':
        saltcmd = [
          self.doBulkLoad,
          'tgt=' + self.taskItem.subdomain,
          'mode=sync'
        ]
      else:
        #print("self: In DO, tasksList sync " + str(self.taskItem) )
        saltcmd = [
          self.doSiteSync,
          'tgt=' + self.taskOptions['subdomain'],
          'site=' + self.taskOptions['site'],
          'mode=all'
        ]

      backup = self.taskOptions.get('backup_param', '')
      if backup != '': saltcmd.append(backup)  

    elif 'deploy' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doSiteDeploy,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site'],
      ]
      backup = self.taskOptions.get('backup_param', '')
      if backup != '': saltcmd.append(backup)  

    elif 'cache' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doCacheClear,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site']
      ]

    elif 'varnish' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doVarnishClear,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site']
      ]

    elif 'rb' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doRollback,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site']
      ]

    elif 'unrb' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doRollback,
        'tgt=' + self.taskOptions['subdomain'],
        'site=' + self.taskOptions['site'],
        'undo'
      ]

    elif 'merge' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doMerge,
        'repo=' + self.taskOptions['mergeRepo'],
        'merge-to=' + self.taskOptions['mergeTo']
      ]
      if self.taskOptions['mergeTest']: saltcmd.append('test')

    elif 'versionup' == tasksList[self.taskItem.task]['do']:
      saltcmd = [
        self.doVersionUpdate,
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
        # if socket.gethostname() == constants.SALT_MASTER_LOCAL:
        #   from saltdev import SaltDev
        #   saltcmd_str = ' '.join(saltcmd)
        #   errors = 0
        #   # relay the commands to the salt_master
        #   output, errors = SaltDev.run_remote(constants.SALT_MASTER, saltcmd_str, errors)
        #   if errors:
        #     errormsg = "Error [SaltTask::do()] SaltDev.run_remote()"
        # else:

        # this is the salt master, issue commandsd to subprocess
        saltcmd[:0] = ['sudo']
        saltcmd_str = ', '.join(saltcmd)
        #self.pushLog.send("saltcmd: " + saltcmd_str)
        output = subprocess.check_output(saltcmd)
      except subprocess.CalledProcessError as e:
        errormsg = saltcmd_str  + "\nError [SaltTask::do()]: " + str(e)
      except Exception as e:
        output = saltcmd_str + "\nError [SaltTask::do()]: ", str(e)
        errormsg = str(e)

    else:
      output = errormsg = "Task not found ({})".format(tasksList[self.taskItem.task])

    #print('SaltTask End of Do')
    return (output, errormsg)
