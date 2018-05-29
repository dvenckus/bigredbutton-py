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
      mdash: { 'name': mdash, 'attributes': 'role="separator" class="divider"' },
      'dev-all': { 'name': "Develop-All", 'attributes': 'class="branch"' },
      'frye': { 'name': "Develop-Frye", 'attributes': 'class="branch"' },
      'gumby': { 'name': "Develop-Gumby", 'attributes': 'class="branch"' },
      'hobbes': { 'name': "Develop-Hobbes", 'attributes': 'class="branch"' },
      'itchy': { 'name': "Develop-Itchy", 'attributes': 'class="branch"' }
    },
    'list_order': ['0', 'stage', 'master', mdash, 'dev-all', 'frye', 'gumby', 'hobbes', 'itchy']
  }

  @staticmethod
  def get():
    ''' returns dictionary of merge targets '''
    return Branches.list

