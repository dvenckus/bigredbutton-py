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
    'ah': { 'name': "Arthritis-health" },
    'oh': { 'name': "Osteoporosis-health" },
    'sh': { 'name': "Spine-health" },
    'sp': { 'name': "Sports-health" },
    'frm': { 'name': 'Forums' }
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
