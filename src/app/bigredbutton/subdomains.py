#
# tasks.py
#

from html.parser import HTMLParser

class SubdomainsList(object):

  mdash = HTMLParser().unescape("&mdash;")

  www = 'www'
  forum_sitecode = 'vf'
  forum = 'forum'

  list = {
    'list': {
      '0': { 'name': mdash + " Select Subdomain " + mdash },
      'eve': { 'name': "Eve" },
      'eve8': { 'name': "Eve8" },
      'demo': { 'name': "Frye/Demo" },
      'itchy': { 'name': "Itchy" },
      'stage': { 'name': "Stage" },
      'master': { 'name': "Master" },
      'www': { 'name': "Production" }
    },
    'list_order': {
      'pre-prod': ['0', 'eve', 'eve8', 'demo', 'itchy', 'stage', 'master'],
      'production': ['www']
    }
  }

  # 'gumby': { 'name': "Gumby" },
  # 'hobbes': { 'name': "Hobbes" },


  @staticmethod
  def get():
    '''
    returns list
    '''
    return SubdomainsList.list



  @staticmethod
  def getSubdomain(sitecode='', selected='', env='pre-prod'):
    if sitecode == '': return ''

    if env == 'prod':
      return SubdomainsList.forum if sitecode == SubdomainsList.forum_sitecode else SubdomainsList.www

    sd = SubdomainsList.list.get('list').get(selected, '')
    if sd != '':
      return selected + '-forum' if sitecode == SubdomainsList.forum_sitecode else selected

    return ''
