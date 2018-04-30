from flask import Flask, current_app, flash, redirect, render_template, Response, request, session, abort, jsonify, url_for
from app.bigredbutton import app, db
from models.meta import Base
from models.user import User
from models.permission import Permission
from passlib.hash import sha256_crypt

from sites import SitesList
from subdomains import SubdomainsList
from tasks import TasksList
from brbqueue import BrbQueue
from push import Push
from repositories import Repositories
from branches import Branches

import json
from datetime import datetime, timedelta
import pytz

from gevent import monkey; monkey.patch_all()
import redis
import re
import sys
import os


# connect to redis server for message stream handling
# unix_socket_path='/var/run/redis/redis.sock'
# remove the unix_socket_path parameter to default to 127.0.0.1:6379
_redis = redis.StrictRedis(unix_socket_path=app.config['REDIS_SOCKET_PATH'])


### NOTE!  Session object only available from within app request functions
### cannot be passed to another function without losing the session data

# BIG RED BUTTON - main page & login page
@app.route('/')
def main_page():
  if session.get('logged_in', None): 
    return render_template('main.html',  sites=SitesList.get(),
                                         tasks=TasksList.get(),
                                         subdomains=SubdomainsList.get(),
                                         repositories=Repositories.get(),
                                         branches=Branches.get(),
                                         queue=BrbQueue.get(),
                                         sse_history=get_sse_history())

  return render_template('login.html')


# LOGIN / LOGOUT
@app.route('/login', methods=['POST'])
def login_page():
    try:
      if 'attempts' not in session: 
        session['attempts'] = 0
        session['username'] = ''
        session['logged_in'] = False
        session['permissions'] = []

      if request.form['username'] != '' and request.form['password'] != '':
        # retrieve the user record
        user = db.session.query(User).filter_by(username=request.form['username']).first()

        if user.password and sha256_crypt.verify(request.form['password'], str(user.password)):
          permissions = db.session.query(Permission).filter_by(role_id=user.role_id).order_by(Permission.id.asc())
      
          permission_list = []
          for p in permissions:
            permission_list.append(p.permission)

          if app.config['PERM_AUTHENTICATED'] in permission_list:
            # valid user and correct permission
            session['username'] = user.username
            session['permissions'] = permission_list
            session['logged_in'] = True
            session['attempts'] = 0
            session['permanent'] = True
            #session.modified = True
      else:
        session['attempts'] += 1

      return redirect("/")
      #render_template('test.html')
    except AttributeError:
      return redirect("/")


@app.route("/logout")
def logout():
  session['username'] = ''
  session['logged_in'] = False
  session['attempts'] = 0
  return redirect("/")



# QUEUE handlers
@app.route('/queue')
def queue_get():
  content = render_template('queue.incl.jinja', queue=BrbQueue.get())
  if not isinstance(content, str):
    content = content.decode('utf-8')
  return json.dumps({'response': True, 'content': content }), 200, {'ContentType':'application/json'}


@app.route('/queue/add', methods = ['POST'])
def queue_add():
  # Get the parsed contents of the form data
  jsonData = request.get_json()
  content = ''
  retn = False
  HttpCode = 200

  if not session.get('logged_in', False): return redirect("/")

  if checkPermission('pre-production', session['permissions']):
    if BrbQueue.add(session['username'], jsonData):
      content = render_template('queue.incl.jinja', queue=BrbQueue.get())
      if not isinstance(content, str):
        content = content.decode('utf-8')
      retn = True
  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json'}


@app.route('/queue/cancel/<id>')
def queue_cancel(id):
  content = ''
  retn = False
  HttpCode = 200

  if not session.get('logged_in', False): return redirect("/")

  if checkPermission('pre-production', session['permissions']):
    if BrbQueue.cancel(id):
      content = render_template('queue.incl.jinja', queue=BrbQueue.get())
      retn = True
      if not isinstance(content, str):
        content = content.decode('utf-8')
  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({ 'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json' }


# PUSH handlers
@app.route('/push', methods = ['POST'])
def push():
  retn = False
  # Get the parsed contents of the form content
  jsonData = request.get_json()
  content = ''
  retn = False
  HttpCode = 200

  if not session.get('logged_in', False): return redirect("/")

  if checkPermission('production', session['permissions']):
    content = Push.do(session['username'], jsonData)
    if content != False:
      retn = True
      if not isinstance(content, str):
        content = content.decode('utf-8')
  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json'}


# SSE (server sent message) handlers
def event_stream():
    channel = app.config['EVENT_STREAM_CHANNEL']
    pubsub = _redis.pubsub()
    pubsub.subscribe(channel)
    for message in pubsub.listen():
        print(message)
        yield "data: %s|%s|%s\n\n" % (message['channel'].decode('utf-8'), message['type'], str(message['data']))

@app.route('/stream')
def stream():
    resp = Response(event_stream(), mimetype="text/event-stream")
    resp.headers['X-Accel-Buffering'] = 'no'
    return resp


def get_sse_history():
  sse_history = []
  keys = _redis.keys('BRB*')
  for key in keys:
    val = _redis.get(key)
    val = val.decode('utf-8')
    sse_history.append(val)

  sse_history.sort()

  return sse_history


#### debug for alerts ####

@app.route('/send')
def send():
  return render_template('send.html')


@app.route('/post', methods=['POST'])
def post():
    channel = app.config['EVENT_STREAM_CHANNEL']
    message = request.form['message']
    now = datetime.now().replace(microsecond=0).time()
    _redis.publish(channel, u'[%s] BigRedButton says: %s' % (now.isoformat(), message))
    resp = Response(status=202)
    resp.headers['X-Accel-Buffering'] = 'no'
    return resp




##############################

# handle session expiration
@app.before_request
def set_session_timeout():
    app.permanent_session_lifetime = timedelta(hours=1)

#@app.before_request
#def force_https():
#    if request.endpoint in app.view_functions and request.headers.get('X-Forwarded-Proto', None) == 'http':
#        return redirect(request.url.replace('http://', 'https://'))

@app.after_request
def add_header(r):
    # block caching of files for now
    #resp.cache_control.max_age = 0
    #resp.cache_control.no-cache = True
    #resp.cache_control.no-store = True
    #resp.cache_control.must-revalidate = True

    r.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    r.headers['Last-Modified'] = datetime.now()
    r.headers['Pragma'] = "no-cache"
    r.headers['Expires'] = "-1"
    r.headers['X-Accel-Buffering'] = 'no'
    return r

# this is a jinja2 custom filter for formatting dates
@app.template_filter('timestamp')
def format_timestamp(d):
    tz = pytz.timezone(app.config['TIMEZONE'])
    return datetime.fromtimestamp(int(d), tz).strftime('%Y-%m-%d %H:%M:%S')


###
# Utilities
###

def checkPermission(permission='', permissions=[]):
  ''' checks the permission and returns True|False accordingly '''
  if permission == '' or permissions == []: return False
  return (permission in permissions)



