#
# sites.py
#
from html.parser import HTMLParser

class SitesList(object):

  mdash = HTMLParser().unescape("&mdash;")

  list = {
    'list': {
      '0': { 'name': mdash + " Select Site " + mdash },
      'all': { 'name': "ALL [ah, ph, sh, sp, vh, vf]" },
      mdash: { 'name': mdash, 'attributes': 'role="separator" class="divider"' },
      'ah': { 'name': "Arthritis-health", 'attributes': 'class="site"' },
      'ph': { 'name': "Pain-health", 'attributes': 'class="site"' },
      'sh': { 'name': "Spine-health", 'attributes': 'class="site"' },
      'sp': { 'name': "Sports-health", 'attributes': 'class="site"' },
      'vh': { 'name': "Veritas Health", 'attributes': 'class="site"'},
      'vf': { 'name': 'Forums', 'attributes': 'class="site"' }
    },
    'list_order': {
      'pre-prod': ['0', 'all', mdash, 'ah', 'ph', 'sh', 'sp', 'vh', 'vf'],
      'production': ['0', 'ah', 'ph', 'sh', 'sp', 'vh', 'vf']
    }
  }

  @staticmethod
  def get():
    '''
    returns dictionary of sites
    '''
    return SitesList.list
