from flask import current_app
from flask import Flask, flash, redirect, render_template, Response, request, session, abort, jsonify

from app.bigredbutton import app, db
from sites import SitesList
from subdomains import SubdomainsList
from tasks import TasksList
from models.meta import Base
from models.user import User
from queue import Queue
from push import Push

import datetime
from passlib.hash import sha256_crypt
from gevent import monkey; monkey.patch_all()
import redis

# connect to redis server for message stream handling
red = redis.StrictRedis()
channel = 'alerts'


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
                                         subdomains_order=SubdomainsList.order(),
                                         queue=Queue.get() )

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


# QUEUE handlers
@app.route('/queue')
def queue_get():
  return render_template('queue.incl.jinja', queue=Queue.get())


@app.route('/queue/add', methods = ['POST'])
def queue_add():
  # Get the parsed contents of the form data
  jsonData = request.json
  content = ''
  retn = False

  if Queue.add(session['username'], jsonData):
    content = render_template('queue.incl.jinja', queue=Queue.get())
    retn = True

  return json.dumps({'success': retn, 'content': content }), 200, {'ContentType':'application/json'}


@app.route('/queue/cancel/<id>')
def queue_cancel(id):
  content = ''
  retn = False

  if Queue.cancel(id):
    content = render_template('queue.incl.jinja', queue=Queue.get())
    retn = True

  return json.dumps({'success': retn, 'content': content}), 200, {'ContentType':'application/json'}


# PUSH handlers
@app.route('/push', methods = ['POST'])
def push():
  retn = False
  # Get the parsed contents of the form content
  jsonData = request.json
  content = ''
  retn = False

  content = Push.do(session['username'], jsonData)
  if content != False: retn = True

  return json.dumps({'success': retn, 'content': content }), 200, {'ContentType':'application/json'}


# SSE (server sent message) handlers
def event_stream():
    pubsub = red.pubsub()
    pubsub.subscribe(channel)
    for message in pubsub.listen():
        print message
        yield "data: %s|%s|%s\n\n" % (message['channel'], message['type'], str(message['data']))

@app.route('/stream')
def stream():
    return Response(event_stream(), mimetype="text/event-stream")

#### debug for alerts ####

@app.route('/send')
def send():
  return render_template('send.html')


@app.route('/post', methods=['POST'])
def post():
    message = request.form['message']
    now = datetime.datetime.now().replace(microsecond=0).time()
    red.publish(channel, u'[%s] BigRedButton says: %s' % (now.isoformat(), message))
    return Response(status=202)

############################

@app.after_request
def add_header(response):
    #block caching of files for now
    response.cache_control.max_age = 0
    return response

# this is a jinja2 custom filter for formatting dates
@app.template_filter('timestamp')
def format_timestamp(d):
    return datetime.datetime.fromtimestamp(int(d)).strftime('%Y-%m-%d %H:%M:%S')
