#
# config.py
#
import os

# Statement for
#  enabling the development environment
DEBUG = True

FLASK_DEBUG = True

# Define the application directory

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

PID_DIR = '/var/run/bigredbutton'
LOG_DIR = '/var/log/bigredbutton'
SCRIPTS_DIR = '/var/www/scripts'

### LOGS ###
LOG_FILE =  LOG_DIR + '/brb-py.log'
ERROR_LOG_FILE =  LOG_DIR + '/brb-py.error.log'

# Queue Manager Logs
QM_PIDFILE = PID_DIR + '/brb_queue_manager.pid'
QM_LOGFILE = LOG_DIR + '/brb_queue_manager.log'

# SaltTask Log
TASK_LOGFILE =  LOG_DIR + '/brb_tasks.log'   

VIRTUAL_ENV = os.environ.get('VIRTUAL_ENV')
BRB_ENV = VIRTUAL_ENV + '/bigredbutton'

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
CSRF_SESSION_KEY = "I_am_not_a_pizza"

# Secret key for signing cookies
SECRET_KEY = "I_am_a_VH_python_app"
#SECRET_KEY = os.urandom(12)

SEND_FILE_MAX_AGE_DEFAULT = 0

SESSION_TYPE = 'redis'

REDIS_SOCKET_PATH = '/var/run/redis/redis.sock'
EVENT_STREAM_CHANNEL = 'alerts'
TIMEZONE = 'America/Chicago'

# email settings
EMAIL_FROM = 'no-reply@bigredbutton.veritashealth.com'
EMAIL_TO = 'dev@veritashealth.com'
EMAIL_ENABLED = True


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




