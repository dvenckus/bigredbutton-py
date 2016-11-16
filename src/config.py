# config.py
# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
# see flask-sqlalchemy settings explained here:  http://flask-sqlalchemy.pocoo.org/2.1/config/
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app', 'bigredbutton', 'database', 'brb.db')
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

SESSION_TYPE = 'redis'
