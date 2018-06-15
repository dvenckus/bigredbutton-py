#
# releases.py
#
import glob
import constants
from os import chdir, getcwd
from html.parser import HTMLParser


class Releases(object):

  @staticmethod
  def get():
    ''' '''
    mdash = HTMLParser().unescape("&mdash;")

    release_scripts = [ mdash + " Select Script " + mdash ]    

    orig_dir = getcwd()
    chdir(constants.RELEASE_SCRIPTS_DIR)

    for filename in glob.iglob('*/*.*_*-release.php', recursive=True):
      f = filename.split('/')
      if f[1]:
        release_scripts.append(f[1])

    chdir(orig_dir)

    return release_scripts
    


