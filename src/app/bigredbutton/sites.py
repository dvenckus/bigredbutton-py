#
# sites.py
#
from HTMLParser import HTMLParser

class SitesList(object):

  mdash = HTMLParser().unescape("&mdash;")

  list = {
    '0': { 'name': mdash + " Select Site " + mdash },
    'all': { 'name': "ALL" },
    mdash: { 'name': mdash, 'attributes': 'role="separator" class="divider"' },
    'ah': { 'name': "Arthritis-health", 'attributes': 'class="site"' },
    'oh': { 'name': "Osteoporosis-health", 'attributes': 'class="site"' },
    'sh': { 'name': "Spine-health", 'attributes': 'class="site"' },
    'sp': { 'name': "Sports-health", 'attributes': 'class="site"' },
    'frm': { 'name': 'Forums', 'attributes': 'class="site"' }
  }

  list_order = {
     'pre-prod': ['0', 'all', mdash, 'ah', 'oh', 'sp', 'sh', 'frm'],
     'production': ['0', 'ah', 'oh', 'sp', 'sh', 'frm']
  }

  @staticmethod
  def get():
    '''
    returns dictionary of sites
    '''
    return SitesList.list

  @staticmethod
  def order():
    '''
    returns order of sites keys
    '''
    return SitesList.list_order
