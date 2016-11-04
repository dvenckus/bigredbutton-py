#
# tasks.py
#

from HTMLParser import HTMLParser

class TasksList(object):

  mdash = HTMLParser().unescape("&mdash;")

  list = {
    '0': { 'name': mdash + " Select Task " + mdash },
    'pepperoni': { 'name': "Pepperoni" },
    'push': { 'name': "Push" },
    'sync': { 'name': "Sync (database + files)" },
    'cache': { 'name': "Cache Clear" },
    'varnish': { 'name': "Varnish Clear" },
    mdash: { 'name': mdash, 'attributes': 'role="separator" class="divider"' },
    'rb': { 'name': 'Rollback' },
    'unrb': { 'name': 'Undo Rollback' }
  }

  list_order = {
    'pre-prod': ['0', 'pepperoni', 'push', 'sync', 'cache', 'varnish', mdash, 'rb', 'unrb'],
    'production': ['0', 'pepperoni', 'push', 'cache', mdash, 'rb', 'unrb']
  }

  @staticmethod
  def get():
    '''
    returns list
    '''
    return TasksList.list

  @staticmethod
  def order():
    '''
    returns order of list keys
    '''

    return TasksList.list_order
