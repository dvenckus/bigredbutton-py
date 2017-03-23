#
# sites.py
#
from html.parser import HTMLParser

class SitesList(object):

  mdash = HTMLParser().unescape("&mdash;")

  www = 'www2'
  forum_sitecode = 'vf'
  forum = 'www2-forum'

  list = {
    '0': { 'name': mdash + " Select Site " + mdash },
    'all': { 'name': "ALL [ah, oh, sh, sp, vf]" },
    mdash: { 'name': mdash, 'attributes': 'role="separator" class="divider"' },
    'ah': { 'name': "Arthritis-health", 'attributes': 'class="site"' },
    'oh': { 'name': "Osteoporosis-health", 'attributes': 'class="site"' },
    'sh': { 'name': "Spine-health", 'attributes': 'class="site"' },
    'sp': { 'name': "Sports-health", 'attributes': 'class="site"' },
    'vh': { 'name': "Veritas Health", 'attributes': 'class=""'},
    'vf': { 'name': 'Forums', 'attributes': 'class="site"' }
  }

  list_order = {
     'pre-prod': ['0', 'all', mdash, 'ah', 'oh', 'sp', 'sh', 'vh', 'vf'],
     'production': ['0', 'ah', 'oh', 'sp', 'sh', 'vh', 'vf']
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

  @staticmethod
  def getProductionSubdomain(sitecode=''):
    if sitecode == '': return ''
    return SitesList.forum if sitecode == SitesList.forum_sitecode else SitesList.www
