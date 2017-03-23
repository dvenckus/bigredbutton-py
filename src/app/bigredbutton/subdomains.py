#
# tasks.py
#

from html.parser import HTMLParser

class SubdomainsList(object):

  mdash = HTMLParser().unescape("&mdash;")

  www = 'www2'
  forum_sitecode = 'vf'
  forum = 'www2-forum'

  list = {
    '0': { 'name': mdash + " Select Subdomain " + mdash },
    'eve': { 'name': "Eve" },
    'frye': { 'name': "Frye" },
    'gumby': { 'name': "Gumby" },
    'hobbes': { 'name': "Hobbes" },
    'itchy': { 'name': "Itchy" },
    'stage': { 'name': "Stage" },
    'master': { 'name': "Master" },
    'www2': { 'name': "Production" },
  }


  list_order = {
    'pre-prod': ['0', 'eve', 'frye', 'gumby', 'hobbes', 'itchy', 'stage', 'master'],
    'production': ['www2']
  }

  @staticmethod
  def get():
    '''
    returns list
    '''
    return SubdomainsList.list

  @staticmethod
  def order():
    '''
    returns order of list keys
    '''
    return SubdomainsList.list_order


  @staticmethod
  def getSubdomain(sitecode='', selected='', env='pre-prod'):
    if sitecode == '': return ''

    if env == 'prod':
      return SubdomainsList.forum if sitecode == SubdomainsList.forum_sitecode else SubdomainsList.www

    sd = SubdomainsList.list.get(selected, '')
    if sd != '':
      return selected + '-forum' if sitecode == SubdomainsList.forum_sitecode else selected

    return ''
