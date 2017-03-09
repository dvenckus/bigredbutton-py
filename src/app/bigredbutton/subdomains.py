#
# tasks.py
#

from html.parser import HTMLParser

class SubdomainsList(object):

  mdash = HTMLParser().unescape("&mdash;")

  list = {
    '0': { 'name': mdash + " Select Subdomain " + mdash },
    'eve': { 'name': "Eve" },
    'frye': { 'name': "Frye" },
    'gumby': { 'name': "Gumby" },
    'hobbes': { 'name': "Hobbes" },
    'itchy': { 'name': "Itchy" },
    'stage': { 'name': "Stage" },
    'master': { 'name': "Master" },
    'www': { 'name': "Production" },
  }


  list_order = {
    'pre-prod': ['0', 'eve', 'frye', 'gumby', 'hobbes', 'itchy', 'stage', 'master'],
    'production': ['www']
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
