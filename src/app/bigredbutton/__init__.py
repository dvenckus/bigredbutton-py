from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from os import sys, path

app = Flask(__name__)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


app.config.from_object('config')
app.secret_key = app.config['SECRET_KEY']

# make sure he bigredbutton model is in the python path
sys.path.append(path.abspath(path.dirname(__file__)))

#print 'BASE_DIR: ' + app.config['BASE_DIR']
#print 'SQLALCHEMY_DATABASE_URI: ' + app.config['SQLALCHEMY_DATABASE_URI']

# connect database
db = SQLAlchemy(app)

db.create_all()

__all__ = ['views', 'SitesList', 'TasksList', 'SubdomainsList', 'Queue', 'Utils']
from app.bigredbutton import views, utils
