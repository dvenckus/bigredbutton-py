#
# releases.py
#
import glob
import constants
from os import chdir, getcwd
import git 
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
    # use the tags from master branch
    # pull the scripts from develop branch
    #chdir(constants.VH_CONFIG_DEV_REPO)
    #cmd = "/usr/bin/git describe --tags `git rev-list --tags --max-count=1`"
    repo = git.Repo(constants.VH_CONFIG_MASTER_REPO)
    last_tag = repo.git.describe('--tags', '--candidates=1')
    last_tag = last_tag[0:7]
    app.logger.info("Repo: {}".format(constants.VH_CONFIG_MASTER_REPO))
    app.logger.info("Lastag: {}".format(last_tag))

    chdir(constants.RELEASE_SCRIPTS_DIR)
    #chdir(constants.DEV_RELEASE_SCRIPTS_DIR)

    for globfile in glob.iglob(last_tag + '/*release.php', recursive=True):
      file = globfile.split('/')
      if file[1]:
        filename = file[1]
        release_scripts[globfile] = filename

    chdir(orig_dir)

    return release_scripts
    


