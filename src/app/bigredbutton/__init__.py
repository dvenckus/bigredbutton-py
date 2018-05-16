from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from os import sys, path
import logging
from logging.handlers import RotatingFileHandler


app = Flask(__name__, static_url_path='')


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


app.config.from_object('constants')
app.secret_key = app.config['SECRET_KEY']
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# make sure he bigredbutton model is in the python path
sys.path.insert(0, './lib')
sys.path.append(path.abspath(path.dirname(__file__)))
sys.path.append(path.abspath(path.dirname(__file__)+'/models'))


# Logging
handler = RotatingFileHandler(app.config['LOG_FILE'], maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)


# connect database
db = SQLAlchemy(app)
db.create_all()


#__all__ = ['views', 'Users', 'SitesList', 'TasksList', 'SubdomainsList', 'BrbQueue', 'Utils']
from app.bigredbutton import views, utils
