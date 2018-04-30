# config.py
# Statement for
#  enabling the development environment
DEBUG = True

FLASK_DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

PID_DIR = '/var/run/bigredbutton'
LOG_DIR = '/var/log/bigredbutton'

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

# user pre-defined roles
ADMIN_ROLE = 1
AUTH_ROLE = 2
ALL_SERVER_ROLE = 3
PRE_PROD_ROLE = 4

# role permissions 
# basic access
PERM_AUTHENTICATED = 'authenticated'

# email settings
EMAIL_FROM = 'bigredbutton@veritashealth.com'
EMAIL_TO = 'dev@veritashealth.com'


