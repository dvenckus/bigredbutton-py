
from flask import current_app
from flask import Flask, flash, redirect, render_template, Response, request, session, abort
#from flask_sqlalchemy import SQLAlchemy

from app.bigredbutton import app, db
from app.bigredbutton.sites import SitesList
from app.bigredbutton.subdomains import SubdomainsList
from app.bigredbutton.tasks import TasksList
from app.bigredbutton.database.user import *


import datetime
from passlib.hash import sha256_crypt
from gevent import monkey; monkey.patch_all()

import redis

# connect to redis server for message stream handling
red = redis.StrictRedis()
channel = 'alerts'
#print app.config['SQLALCHEMY_DATABASE_URI']


# BIG RED BUTTON - main page
@app.route('/')
def main_page():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    return render_template('main.html',  sites=SitesList.get(),
                                         sites_order=SitesList.order(),
                                         tasks=TasksList.get(),
                                         tasks_order=TasksList.order(),
                                         subdomains=SubdomainsList.get(),
                                         subdomains_order=SubdomainsList.order() )

# LOGIN / LOGOUT
@app.route('/login', methods=['POST'])
def login_page():
    #print "login key: " + str(app.secret_key)
    if request.form['password'] != '' and request.form['username'] != '':
      user = db.session.query(User).filter_by(username=request.form['username']).first()
      if sha256_crypt.verify(request.form['password'], str(user.password)):
        session['username'] = request.form['username']
        session['logged_in'] = True
        session['attempts'] = 0
      else:
        if 'attempts' not in session : session['attempts'] = 0
        session['attempts'] += 1
    else:
      if 'attempts' not in session : session['attempts'] = 0
      session['attempts'] += 1
    return redirect("/")


@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['attempts'] = 0
    return redirect("/")


# SSE (server sent message) handlers
def event_stream():
    pubsub = red.pubsub()
    pubsub.subscribe(channel)
    for message in pubsub.listen():
        print message
        yield "data: %s|%s|%s\n\n" % (message['channel'], message['type'], str(message['data']))


@app.route('/send')
def send():
  return render_template('messagetest.html')


@app.route('/post', methods=['POST'])
def post():
    message = request.form['message']
    now = datetime.datetime.now().replace(microsecond=0).time()
    red.publish(channel, u'[%s] BigRedButton says: %s' % (now.isoformat(), message))
    return Response(status=202)


@app.route('/stream')
def stream():
    return Response(event_stream(), mimetype="text/event-stream")


@app.after_request
def add_header(response):
    #block caching of files for now
    response.cache_control.max_age = 0
    return response
