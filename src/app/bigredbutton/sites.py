#
# sites.py
#
from html.parser import HTMLParser

class SitesList(object):

  mdash = HTMLParser().unescape("&mdash;")

  list = {
    'list': {
      '0': { 'name': mdash + " Select Site " + mdash },
      'all': { 'name': "ALL D7 Sites [ah, ph, sh, sp, vh]" },
      'health': { 'name': "All D7 Healthsites [ah, ph, sh, sp]" },
      'vc': { 'name': "All D8 Veritas-Core Sites [ah, ph, sh, sp, vh]"},
      '-': { 'name': mdash, 'attributes': 'role="separator" class="divider"' },
      'ah': { 'name': "Arthritis-health", 'attributes': 'class="site health"' },
      'ph': { 'name': "Pain-health", 'attributes': 'class="site health"' },
      'sh': { 'name': "Spine-health", 'attributes': 'class="site health"' },
      'sp': { 'name': "Sports-health", 'attributes': 'class="site health"' },
      'vh': { 'name': "Veritas Health", 'attributes': 'class="site"'}
    },
    'list_order': {
      'pre-prod': ['0', 'all', 'vc', 'health', '-', 'ah', 'ph', 'sh', 'sp', 'vh'],
      'production': ['0', 'ah', 'ph', 'sh', 'sp', 'vh']
    }
  }

  @staticmethod
  def get():
    '''
    returns dictionary of sites
    '''
    return SitesList.list
