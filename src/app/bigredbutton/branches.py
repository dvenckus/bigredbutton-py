#
# mergelist.py
#
from html.parser import HTMLParser

class Branches(object):

  mdash = HTMLParser().unescape("&mdash;")

  list = {
    'list': { 
      '0': { 'name': mdash + " Select Branch " + mdash },
      'stage': { 'name': "Stage", 'attributes': 'class="branch"' },
      'master': { 'name': "Master", 'attributes': 'class="branch"' },
    },
    'list_order': ['0', 'stage', 'master']
  }

  @staticmethod
  def get():
    ''' returns dictionary of merge targets '''
    return Branches.list

