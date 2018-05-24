from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.orm import sessionmaker
from os import sys, path
import logging
from logging.handlers import RotatingFileHandler


app = Flask(__name__, static_url_path='')

app.config.from_object('constants')

# make sure he bigredbutton model dir + saltlibs dir is in the python path
app_bigredbutton_dir = path.abspath(path.dirname(__file__))
scripts_dir = app.config['SCRIPTS_DIR']
dev_saltlibs = app.config['DEV_SALTLIBS']

sys.path.insert(0, './lib')
sys.path.append(app_bigredbutton_dir)
sys.path.append(app_bigredbutton_dir + '/models')
sys.path.append(scripts_dir + '/saltlibs')
sys.path.append(dev_saltlibs)

app.secret_key = app.config['SECRET_KEY']

# Logging - set up log for access wherever app is imported
handler = RotatingFileHandler(app.config['LOG_FILE'], maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)


# connect database
db = SQLAlchemy(app)
db.create_all()

# Important!!  This loads the views and page handlers
from app.bigredbutton import views, utils
