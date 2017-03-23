#
# tasks.py
#

from html.parser import HTMLParser

class TasksList(object):

  mdash = HTMLParser().unescape("&mdash;")

  list = {
    '0': { 'name': mdash + " Select Task " + mdash, 'do': ''  },
    'pepperoni': { 'name': "Pepperoni", 'do': '' },
    'push': { 'name': "Push", 'do': 'deploy' },
    'sync': { 'name': "Sync (database + files)", 'do': 'sync' },
    'cache': { 'name': "Cache Clear", 'do': 'cache'},
    'varnish': { 'name': "Varnish Clear", 'do': 'varnish' },
    #mdash: { 'name': mdash, 'attributes': 'role="separator" class="divider"', 'do': '' },
    #'rb': { 'name': 'Rollback', 'do': 'rb'},
    #'unrb': { 'name': 'Undo Rollback', 'do': 'unrb' }
  }

  list_order = {
    'pre-prod': ['0', 'push', 'sync', 'cache'], 
    #, mdash, 'rb', 'unrb'],
    'production': ['0', 'push', 'cache', 'varnish']
    #, mdash, 'rb', 'unrb']
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
