#
# repositories.py
#
from html.parser import HTMLParser

class Repositories(object):

  mdash = HTMLParser().unescape("&mdash;")

  list = {
    'list': {
      '0': { 'name': mdash + " Select Repository " + mdash },
      'all': { 'name': "All", 'attributes': 'class="repo"' },
      'h+p': { 'name': "Healthsites + Profile", 'attributes': 'class="repo"' },
      'pr': { 'name': "Profile", 'attributes': 'class="repo"' },
      'ah': { 'name': "Arthritis-health", 'attributes': 'class="repo"' },
      'ph': { 'name': "Pain-health", 'attributes': 'class="repo"' },
      'sh': { 'name': "Spine-health", 'attributes': 'class="repo"' },
      'sp': { 'name': "Sports-health", 'attributes': 'class="repo"' },
      'vh': { 'name': "Veritashealth", 'attributes': 'class="repo"'},
      'vf': { 'name': 'Forums', 'attributes': 'class="repo"' },
      'vc': { 'name': 'Veritas Health Config', 'attributes': 'class="repo"' },
      'brb': { 'name': 'BigRedButton', 'attributes': 'class="repo"' }
    },
    'list_order': ['0', 'all', 'h+p', 'pr', 'ah', 'ph', 'sh', 'sp', 'vh', 'vf', 'vc', 'brb']
  }

  @staticmethod
  def get():
    ''' returns dictionary of merge targets '''
    return Repositories.list

