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
      'health': { 'name': "All Healthsites [ah, ph, sh, sp]" },
      '-': { 'name': mdash, 'attributes': 'role="separator" class="divider"' },
      'ah': { 'name': "Arthritis-health", 'attributes': 'class="site health"' },
      'ph': { 'name': "Pain-health", 'attributes': 'class="site health"' },
      'sh': { 'name': "Spine-health", 'attributes': 'class="site health"' },
      'sp': { 'name': "Sports-health", 'attributes': 'class="site health"' },
      'vh': { 'name': "Veritas Health", 'attributes': 'class="site"'},
      'vf': { 'name': 'Forums', 'attributes': 'class="site"' }
    },
    'list_order': {
      'pre-prod': ['0', 'all', 'health', '-', 'ah', 'ph', 'sh', 'sp', 'vh', 'vf'],
      'production': ['0', 'ah', 'ph', 'sh', 'sp', 'vh', 'vf']
    }
  }

  @staticmethod
  def get():
    '''
    returns dictionary of sites
    '''
    return SitesList.list
