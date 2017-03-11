#
# tasks.py
#

from html.parser import HTMLParser

class SubdomainsList(object):

  mdash = HTMLParser().unescape("&mdash;")

  list = {
    '0': { 'name': mdash + " Select Subdomain " + mdash },
    'eve2': { 'name': "Eve" },
    'frye': { 'name': "Frye" },
    'gumby': { 'name': "Gumby" },
    'hobbes': { 'name': "Hobbes" },
    'itchy': { 'name': "Itchy" },
    'stage2': { 'name': "Stage" },
    'master2': { 'name': "Master" },
    'www2': { 'name': "Production" },
  }


  list_order = {
    'pre-prod': ['0', 'eve2', 'frye', 'gumby', 'hobbes', 'itchy', 'stage2', 'master2'],
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
