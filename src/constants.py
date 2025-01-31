#
# config.py
#
import os

# Statement for
#  enabling the development environment
DEBUG = True
FLASK_DEBUG = True

#PYTHONUNBUFFERED = True
#CACHE_TYPE = None
TEMPLATES_AUTO_RELOAD = True


TIMEZONE = 'America/Chicago'

# Define the application directory

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

PID_DIR = '/var/run/bigredbutton'
LOG_DIR = '/var/log/bigredbutton'
SCRIPTS_DIR = '/var/www/scripts'
VH_CONFIG_MASTER_REPO = '/srv/salt/repos/veritashealth/veritas-health-config/master'
VH_CONFIG_DEV_REPO = '/srv/salt/repos/veritashealth/veritas-health-config/develop'
VERITAS_PROFILE_REPO = '/srv/salt/repos/veritashealth/veritas-profile-d7/develop'
SALT_SCRIPTS_DIR = '/srv/salt/base/assets/scripts'

DEV_VH_CONFIG_REPO = '/mnt/hgfs/veritashealth/salt/veritas-health-config'
DEV_SCRIPTS_DIR = DEV_VH_CONFIG_REPO + '/saltstack/srv/salt/base/assets/scripts'

SALTLIBS = SCRIPTS_DIR + '/saltlibs'

DEV_SALTLIBS = DEV_SCRIPTS_DIR + '/master/saltlibs'
DEVLIBS = DEV_SCRIPTS_DIR + '/local/devlibs'
DEVSCRIPTS = DEV_SCRIPTS_DIR + '/local'

RELEASE_SCRIPTS_DIR = VH_CONFIG_DEV_REPO + '/releases'
DEV_RELEASE_SCRIPTS_DIR = DEV_VH_CONFIG_REPO + '/releases'

# salt scripts
SCRIPT_SITE_SYNC = SCRIPTS_DIR + '/brb_site_sync.py'
SCRIPT_SITE_DEPLOY = SCRIPTS_DIR + '/brb_site_deploy.py'
SCRIPT_SITE_RELEASE = SCRIPTS_DIR + '/brb_site_release.py'
SCRIPT_MIGRATE = SCRIPTS_DIR + '/brb_site_migrations.py'
SCRIPT_CACHE_CLEAR = SCRIPTS_DIR + '/brb_site_cache_clear.py'
SCRIPT_VARNISH_CLEAR = SCRIPTS_DIR + '/brb_varnish_clear.py'
SCRIPT_ROLLBACK = SCRIPTS_DIR + '/brb_site_rollback.py'
SCRIPT_BULK_LOAD = SCRIPTS_DIR + '/brb_bulk_load.py'
SCRIPT_MERGE_REPOS = SCRIPTS_DIR + '/brb_merge_repos.py'
SCRIPT_VERSION_UPDATE = SCRIPTS_DIR + '/brb_version_update.py'
SCRIPT_RELEASE_SCRIPT = SCRIPTS_DIR + '/brb_release_script.py'

### LOGS ###
LOG_FILE =  LOG_DIR + '/bigredbutton.log'

# Queue Manager Logs
QM_PIDFILE = PID_DIR + '/brb_queue_manager.pid'
QM_LOGFILE = LOG_DIR + '/brb_queue_manager.log'

# SaltTask Log
TASK_LOGFILE =  LOG_DIR + '/brb_tasks.log'   

# Virtual Env - so bigredbutton can find all of its libraries
#VIRTUAL_ENV = os.environ.get('VIRTUAL_ENV')
VIRTUAL_ENV = '/usr/local/python_virtualenv/bigredbutton'
VIRTUAL_ENV_LIBS = VIRTUAL_ENV + '/lib/python3.6/site-packages'
BRB_ENV = VIRTUAL_ENV

SALT_MASTER = 'boss'
SALT_MASTER_LOCAL = 'dev-boss'

# Define the database - we are working with
# SQLite for this example
# see flask-sqlalchemy settings explained here:  http://flask-sqlalchemy.pocoo.org/2.1/config/
DATABASE_PATH = '/usr/local/sqlite/bigredbutton/brb.db'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
# this adds a lot of overhead -- set to True if you need to for debugging, but don't leave it on
SQLALCHEMY_TRACK_MODIFICATIONS = False
#DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "Its_whats_for_dinner"

# Secret key for signing cookies
SECRET_KEY = "Oy_my_aching_back"
#SECRET_KEY = os.urandom(12)

SEND_FILE_MAX_AGE_DEFAULT = 0

# REDIS - SSE SETTINGS
SESSION_TYPE = 'redis'

CHANNEL_ALERT = 'alerts'
CHANNEL_ALERT_KEY_PREFIX = "BRB_ALERT"
CHANNEL_ALERT_EXPIRES = 3600  #  1 hour

CHANNEL_LOG = 'logstream'
CHANNEL_LOG_KEY_PREFIX = "BRB_LOGSTREAM"
CHANNEL_LOG_EXPIRES = 3600   # 1 hours

CHANNEL_QUEUE = "queue"
CHANNEL_QUEUE_KEY_PREFIX = "BRB_QUEUE"
CHANNEL_QUEUE_EXPIRES = 30 #sec

CHANNEL_DEFAULT = CHANNEL_LOG


# email settings
EMAIL_FROM = 'no-reply@bigredbutton.veritashealth.com'
EMAIL_TO = 'dev@veritashealth.com'
EMAIL_ENABLED = False

USERNAME_DEFAULT='root'

MAX_TASK_HISTORY = 100

# tasks
TASK_BULKLOAD = 'bulkload'
TASK_DEPLOY = 'deploy'
TASK_SYNC = 'sync'
TASK_MSYNC = 'msync'
TASK_MIGRATE = 'migrate'
TASK_CACHE = 'cache'
TASK_VARNISH = 'varnish'
TASK_MERGE = 'merge'
TASK_VERSION_UPDATE = 'versionup'
TASK_RELEASE_SITE = 'relsite'
TASK_RELEASE_SCRIPT = 'relscript'
TASK_ROLLBACK = 'rollback'
TASK_ROLLBACK_UNDO = 'unrb'

# TASKOPT_MERGE_REPO = 'mergeRepo'
# TASKOPT_MERGE_TO = 'mergeTo'
# TASKOPT_MERGE_TEST = 'mergeTest'



########## ROLE & PERMISSION SEED DATA ###########

# user pre-defined roles
# custom roles can be created in addition to these
ROLE_ADMIN = 1
ROLE_AUTHENTICATED = 2
ROLE_ALL_SERVER = 3
ROLE_PRE_PRODUCTION = 4

ROLE_VALUES = {
  ROLE_ADMIN: 'Administrator',
  ROLE_AUTHENTICATED: 'Authenticated',
  ROLE_ALL_SERVER: 'All Server Access',
  ROLE_PRE_PRODUCTION: 'Pre-Production Access'
}

# role permissions 
# defined here because if the permission is not referenced
# in the code, what's the point?
PERMISSION_PRODUCTION = 1
PERMISSION_PRE_PRODUCTION = 2
PERMISSION_MERGE_REPOS = 3
PERMISSION_VERSION_UPDATE = 4
PERMISSION_USER_MANAGEMENT = 5
PERMISSION_AUTHENTICATED = 6
PERMISSION_VALUES = {
  PERMISSION_AUTHENTICATED: 'authenticated',
  PERMISSION_PRE_PRODUCTION: 'pre-production',
  PERMISSION_PRODUCTION: 'production',
  PERMISSION_USER_MANAGEMENT: 'user management',
  PERMISSION_MERGE_REPOS: 'merge repositories',
  PERMISSION_VERSION_UPDATE: 'version update'
}

ROLE_PERMISSION_VALUES = {
  ROLE_ADMIN: [
    PERMISSION_PRODUCTION,
    PERMISSION_PRE_PRODUCTION,
    PERMISSION_MERGE_REPOS,
    PERMISSION_VERSION_UPDATE,
    PERMISSION_USER_MANAGEMENT,
    PERMISSION_AUTHENTICATED
  ],
  ROLE_AUTHENTICATED: [
    PERMISSION_AUTHENTICATED
  ],
  ROLE_ALL_SERVER: [
    PERMISSION_PRODUCTION,
    PERMISSION_PRE_PRODUCTION,
    PERMISSION_MERGE_REPOS, 
    PERMISSION_VERSION_UPDATE,
    PERMISSION_AUTHENTICATED
  ],
  ROLE_PRE_PRODUCTION: [
    PERMISSION_PRE_PRODUCTION,
    PERMISSION_AUTHENTICATED
  ]
}




