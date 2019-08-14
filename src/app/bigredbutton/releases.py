#
# releases.py
#
import glob
import constants
from os import chdir, getcwd, popen
from html.parser import HTMLParser
from app.bigredbutton import app

class Releases(object):

  @staticmethod
  def get():
    ''' '''
    mdash = HTMLParser().unescape("&mdash;")

    release_scripts = {
      0: mdash + " Select Script " + mdash
    }

    orig_dir = getcwd()

    # D7 release versions are based on the veritas-profile-d7 repo
    chdir(constants.VERITAS_PROFILE_REPO)
    cmd = "/usr/bin/git describe --tags `git rev-list --tags --max-count=1`"
    last_version_tag = popen(cmd).read()
    last_version_tag = last_version_tag[0:7]
    #app.logger.info("LastVersionTag: {}".format(last_version_tag))

    chdir(constants.RELEASE_SCRIPTS_DIR)
    #chdir(constants.DEV_RELEASE_SCRIPTS_DIR)

    for globfile in glob.iglob(last_version_tag + '/*release.php', recursive=True):
      file = globfile.split('/')
      if file[1]:
        filename = file[1]
        release_scripts[globfile] = filename

    chdir(orig_dir)

    return release_scripts
    


