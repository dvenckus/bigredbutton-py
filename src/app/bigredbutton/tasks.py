#
# tasks.py
#

from html.parser import HTMLParser
import constants


class TasksList(object):

  mdash = HTMLParser().unescape("&mdash;")

  list = {
    'list': {
      '0': { 'name': mdash + " Select Task " + mdash, 'do': ''  },
      'pepperoni': { 'name': "Pepperoni", 'do': '', 'attributes': '' },
      'push': { 'name': "Push", 'do': constants.TASK_DEPLOY, 'attributes': 'class="task"' },
      'sync': { 'name': "Sync (database + files)", 'do': constants.TASK_SYNC, 'attributes': 'class="task"' },
      'msync': { 'name': "Sync Migration Source Database", 'do': constants.TASK_MSYNC, 'attributes': 'class="task"' },
      'migrate': { 'name': "Migrate D7 --> D8", 'do': constants.TASK_MIGRATE, 'attributes': 'class="task"' },
      'cache': { 'name': "Cache Clear", 'do': constants.TASK_CACHE, 'attributes': 'class="task"' },
      'varnish': { 'name': "Varnish Clear", 'do': constants.TASK_VARNISH, 'attributes': 'class="task"' },
      'merge': { 'name': 'Merge Repositories', 'do': constants.TASK_MERGE, 'attributes': 'class="task"' },
      'versionup': { 'name': 'Release Version Update', 'do': constants.TASK_VERSION_UPDATE, 'attributes': 'class="task"' },
      '-': { 'name': mdash, 'attributes': 'role="separator" class="divider"', 'do': '' },
      'rollback': { 'name': 'Rollback', 'do': constants.TASK_ROLLBACK, 'attributes': 'class="task"'},
      'unrb': { 'name': 'Undo Rollback', 'do': constants.TASK_ROLLBACK_UNDO,  'attributes': 'class="task"' }
    },
    'list_order': {
      'pre-prod': ['0', 'push', 'sync', 'msync', 'migrate', 'cache', '-', 'rollback', 'unrb'],
      'production': ['0', 'push', 'cache', 'varnish', '-', 'rollback', 'unrb']
    }
  }


  @staticmethod
  def get():
    '''
    returns list
    '''
    return TasksList.list

  @staticmethod
  def getList():
    '''
    returns list
    '''
    return TasksList.list['list']

  @staticmethod
  def getListItem(key):
    '''
    returns dictionary for list item
    '''
    item = {}
    try:
      item = TasksList.list['list'][key]
    except KeyError:
      item = {}
    return item

  @staticmethod
  def getListOrder():
    '''
    returns list
    '''
    return TasksList.list['list_order']
