#
# tasks.py
#

from html.parser import HTMLParser

class TasksList(object):

  mdash = HTMLParser().unescape("&mdash;")

  list = {
    'list': {
      '0': { 'name': mdash + " Select Task " + mdash, 'do': ''  },
      'pepperoni': { 'name': "Pepperoni", 'do': '', 'attributes': '' },
      'push': { 'name': "Push", 'do': 'deploy', 'attributes': 'class="task"' },
      'sync': { 'name': "Sync (database + files)", 'do': 'sync', 'attributes': 'class="task"' },
      'cache': { 'name': "Cache Clear", 'do': 'cache', 'attributes': 'class="task"' },
      'varnish': { 'name': "Varnish Clear", 'do': 'varnish', 'attributes': 'class="task"' },
      #mdash: { 'name': mdash, 'attributes': 'role="separator" class="divider"', 'do': '' },
      #'rb': { 'name': 'Rollback', 'do': 'rb'},
      #'unrb': { 'name': 'Undo Rollback', 'do': 'unrb' }
    },
    'list_order': {
      'pre-prod': ['0', 'push', 'sync', 'cache'], 
      #, mdash, 'rb', 'unrb'],
      'production': ['0', 'push', 'cache', 'varnish']
      #, mdash, 'rb', 'unrb']
    }
  }


  @staticmethod
  def get():
    '''
    returns list
    '''
    return TasksList.list
