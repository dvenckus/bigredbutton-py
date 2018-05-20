#
# salttask.py
#
# called by queue_manager
#
import subprocess
import constants
from tasks import TasksList
from pushlog import PushLog


# connect to redis server for message stream handling

class SaltTask(object):

  scripts_dir = constants.SCRIPTS_DIR + '/'

  doSiteSync = scripts_dir + 'brb_site_sync.py'
  doSiteDeploy = scripts_dir + 'brb_site_deploy.py'
  doCacheClear = scripts_dir + 'brb_site_cache_clear.py'
  doVarnishClear = scripts_dir + 'brb_varnish_clear.py'
  doRollback = scripts_dir + 'brb_site_rollback.py'
  doBulkLoad = scripts_dir + 'brb_bulk_load.py'
  doMerge = scripts_dir + 'brb_merge.py'
  doVersionUpdate = scripts_dir + 'brb_version_update.py'

  taskItem = None
  taskOptions = None
  taskDesc = ''
  taskMode = ''
  
  pushLog = None


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

    self.taskOptions['backup_param'] = 'backup' if self.taskOptions.get('dbbackup', False) == True else ''

    self.taskDesc = "({}) {} {} {} {}".format(
                  taskItem.username, 
                  self.taskOptions.get('subdomain', ''), 
                  self.taskOptions.get('site', ''), 
                  taskItem.task, 
                  self.taskOptions.get('backup_param', ''))

    # Alert Channel messages are sent from here
    # Log Channel messages are sent from lower-level BRB salt scripts
    self.pushLog = PushLog(PushLog.CHANNEL_ALERT)
    


  def run(self):
    ''' runs the tasks requested through BRB '''
    # local vars
    output = ''
    errormsg = ''

    ### run the task
    try:
      self.pushLog.start(self.taskDesc)
      self.pushLog.send('BEGIN TASK ' + self.taskDesc)

      output, errormsg = self.do()

      self.pushLog.send(output)

      if len(errormsg):
        self.pushLog.send('An Error occurred ' + str(errormsg))

      self.pushLog.send("END TASK with {} {}".format('ERROR' if len(errormsg) else 'SUCCESS', self.taskDesc))
      self.pushLog.end(self.taskDesc)


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

      if self.taskItem.site == 'vf':
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
        saltcmd[:0] = ['sudo']
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

    #print('SaltTask End of Do')
    return (output, errormsg)
