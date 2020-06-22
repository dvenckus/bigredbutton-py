from flask import Flask, current_app, flash, redirect, render_template, Response, request, session, abort, jsonify, url_for
from app.bigredbutton import app, db
from admin import Admin

#from models.meta import Base
from models.permission import Permission
from models.role import Role
from models.rolepermission import RolePermission
from models.taskhistoryitem import TaskHistoryItem
from models.user import User

from sites import SitesList
from subdomains import SubdomainsList
from tasks import TasksList
from brbqueue import BrbQueue
from push import Push
from repositories import Repositories
from branches import Branches
from taskhistory import TaskHistory 
from utils import Utils
from releases import Releases
from pushlog import PushLog

import json
from datetime import datetime, timedelta
import pytz

#from gevent import monkey; monkey.patch_all()
import redis
import re
import sys
import os
import subprocess
import distro

import logging



# connect to redis server for message stream handling
# unix_socket_path='/var/run/redis/redis.sock'
# remove the unix_socket_path parameter to default to 127.0.0.1:6379
linux_distro = distro.linux_distribution()
redis_socket_path =  '/var/run/redis/redis.sock' if ('CentOS' in linux_distro) else '/var/run/redis/redis-server.sock'

_redis = redis.StrictRedis(unix_socket_path=redis_socket_path)


# Basic HTTP error handling
@app.errorhandler(404)
def not_found(error):
  ''' not_found '''
  return render_template('404.html'), 404


### NOTE!  Session object only available from within app request functions
### cannot be passed to another function without losing the session data

# BIG RED BUTTON - main page & login page
@app.route('/')
def main_page():
  ''' main_page '''
  if session.get('logged_in', None): 
    users = None
    roles = None
    permissions = None
    rolesPermissions = None

    # run the QueueManager in the event any jobs are waiting to be processed
    BrbQueue.runQueueManager()

    if Admin.checkPermission(session.get('user', None), 'PERM_USER_MANAGEMENT', session['permissions']):
      users = Admin.getUsers()
      roles = Admin.getRoles()
      permissions = Admin.getPermissions()
      rolesPermissions = Admin.getRolesPermissions()
      #rolesPermissions = Admin.getRolePermissions(session['user'].role_id)

    #app.logger.info('users: {}'.format(str(users)))
    #app.logger.info('roles: {}'.format(str(roles)))
    #app.logger.info('permissions: {}'.format(str(permissions)))
    #app.logger.info('rolesPermissions: {}'.format(str(rolesPermissions)))
    #app.logger.info('rolesPermissions: {}'.format(str(rolesPermissions)))

    return render_template('main.html',  sites=SitesList.get(),
                                        tasks=TasksList.get(),
                                        releases=Releases.get(),
                                        subdomains=SubdomainsList.get(),
                                        repositories=Repositories.get(),
                                        branches=Branches.get(),
                                        users=users,
                                        roles=roles,
                                        permissions=permissions,
                                        roles_permissions=rolesPermissions,
                                        queue=BrbQueue.get(),
                                        task_history=TaskHistory.get(),
                                        sse_history=get_sse_history(),
                                        log_history=get_log_history(),
                                        constants=app.config)

  return render_template('login.html')


# LOGIN / LOGOUT
@app.route('/login', methods=['POST'])
def login_page():
    try:

      init_session(request.form['username'], request.form['password'])

      return redirect("/")
      #render_template('test.html')
    except AttributeError:
      app.logger.error("Login Invalid")
      return redirect("/")
    except Exception as e:
      app.logger.error('Error: {}'.format(str(e)))
      return redirect("/")


@app.route("/logout")
def logout():
  session['username'] = ''
  session['logged_in'] = False
  session['attempts'] = 0
  return redirect("/")


def init_session(input_username='', input_password = ''):
  '''
  sets up the user session
  returns True if session is valid
  '''
  if 'attempts' not in session: 
    session['attempts'] = 0
    session['username'] = ''
    session['logged_in'] = False
    session['permissions'] = []

  userSession = Admin.validateUser(input_username, input_password)
  
  if userSession and userSession['valid']:
    app.logger.info("user session is valid")
    session['user'] = userSession['user'].toDict()
    session['user']['role'] = userSession['user'].role.toDict()
    session['permissions'] = userSession['permissions']
    session['logged_in'] = True
    session['attempts'] = 0
    session['permanent'] = True
    #app.logger.info("User: {}".format(str(session['user'])))
    return True
  else:
    app.logger.info("user session is not valid")
    session['attempts'] += 1
  
  return False



#----------------------- QUEUE handlers --------------------------
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
  api_request = False

  app.logger.info("Views::queue_add {}".format(jsonData))

  if 'username' in jsonData and jsonData['username'] == 'api_request':
    # open local request api session
    init_session(jsonData['username'], jsonData['password'])
    app.logger.info("User Session Created: {}".format(session.get('logged_in', False)))
    jsonData['password'] = 'xxxxxxx'   # blank password
    api_request = True
   
  if not session.get('logged_in', False):
    if api_request: 
      content = 'Not Authorized'
      HttpCode = 444
      return json.dumps({'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json'}
    else:
      return redirect("/")

  user = session.get('user', None)

  if Admin.checkPermission(user, 'PERMISSION_PRE_PRODUCTION', session['permissions']):
    if BrbQueue.add(user.get('username', ''), jsonData):
      if not api_request:
        # api requests don't require return queue content other than confirmation of success
        queueContent = BrbQueue.get()
        #app.logger.info("Queue Content: {}".format(queueContent))
        content = render_template('queue.incl.jinja', queue=queueContent)
        if not isinstance(content, str):
          content = content.decode('utf-8')
        queue_update(content)

      BrbQueue.runQueueManager(delay=3)
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

  if Admin.checkPermission(session.get('user', None), 'PERMISSION_PRE_PRODUCTION', session['permissions']):
    if BrbQueue.cancel(id):
      content = render_template('queue.incl.jinja', queue=BrbQueue.get())
      retn = True
      if not isinstance(content, str):
        content = content.decode('utf-8')
      
      queue_update(content)
      
  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({ 'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json' }


def queue_update(queueContent=''):
  ''' 
  sends the queue updates via redis pubsub as sse stream from redis pubsub 
  doesn't work and play well (causes blocking) with ajax response updates
  '''
  pushLog = PushLog(app.config['CHANNEL_QUEUE'])
  pushLog.pushMessage(queueContent)
  resp = Response(status=202)
  resp.headers['X-Accel-Buffering'] = 'no'
  return resp



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

  if Admin.checkPermission(session.get('user', None), 'PERMISSION_PRODUCTION', session['permissions']):
    content = Push.do(session['user']['username'], jsonData)
    if content != False:
      retn = True
      if content and not isinstance(content, str):
        content = content.decode('utf-8')
  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json'}


# @app.route('/relscripts')
# def release_scripts():
#   content = Releases.get()
#   # if not isinstance(content, str):
#   #   content = content.decode('utf-8')
#   return json.dumps({'response': True, 'content': content }), 200, {'ContentType':'application/json'}



# ------------------ TOOLS handlers ----------------------------------

# Merge

@app.route('/merge', methods = ['POST'])
def merge():
  retn = False
  # Get the parsed contents of the form content
  jsonData = request.get_json()
  content = ''
  retn = False
  HttpCode = 200

  if not session.get('logged_in', False): return redirect("/")

  app.logger.info("Merge: {}".format(jsonData))

  if Admin.checkPermission(session.get('user', None), 'PERMISSION_MERGE_REPOS', session['permissions']):
    content = Push.do(session['user']['username'], jsonData)
    if content != False:
      retn = True
      if content and not isinstance(content, str):
        content = content.decode('utf-8')
        
  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json'}



# Version

@app.route('/versionup', methods = ['POST'])
def version_update():
  retn = False
  # Get the parsed contents of the form content
  jsonData = request.get_json()
  content = ''
  retn = False
  HttpCode = 200

  if not session.get('logged_in', False): return redirect("/")

  app.logger.info("VersionUpdate: {}".format(jsonData))

  if Admin.checkPermission(session.get('user', None), 'PERMISSION_VERSION_UPDATE', session['permissions']):
    content = Push.do(session['user']['username'], jsonData)
    if content != False:
      retn = True
      if content and not isinstance(content, str):
        content = content.decode('utf-8')
        
  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json'}



# Users

@app.route('/user', methods = ['POST'])
def user_save():
  retn = False
  # Get the parsed contents of the form content
  jsonData = request.get_json()
  content = ''
  retn = False
  HttpCode = 200

  if not session.get('logged_in', False): return redirect("/")

  # uncomment as needed, outputs raw passwords into the log
  #app.logger.info("User Save: {}".format(jsonData))
  

  if Admin.checkPermission(session.get('user', None), 'PERMISSION_USER_MANAGEMENT', session['permissions']):
    if Admin.userSave(session['user']['id'], jsonData):
      content = render_template('users_current.incl.jinja', users=Admin.getUsers())
      retn = True  
      if not isinstance(content, str):
        content = content.decode('utf-8')

  elif int(session['user']['id']) == int(jsonData['user_id']):
    # non-admin user updating own account, this is ok
    if Admin.userSave(session['user']['id'], jsonData):
      retn = True
      content = "Account updated!"

  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json'}


@app.route('/user/delete/<id>')
def user_delete(id):
  content = ''
  retn = False
  HttpCode = 200

  if not session.get('logged_in', False): return redirect("/")

  if Admin.checkPermission(session.get('user', None), 'PERMISSION_USER_MANAGEMENT', session['permissions']):
    if Admin.userDelete(id):
      content = render_template('users_current.incl.jinja', users=Admin.getUsers())
      retn = True
      if not isinstance(content, str):
        content = content.decode('utf-8')
        
  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({ 'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json' }


# Roles

@app.route('/role', methods = ['POST'])
def role_save():
  retn = False
  # Get the parsed contents of the form content
  jsonData = request.get_json()
  content = ''
  retn = False
  HttpCode = 200

  if not session.get('logged_in', False): return redirect("/")

  app.logger.info("Role Save: {}".format(jsonData))

  if Admin.checkPermission(session.get('user', None), 'PERMISSION_USER_MANAGEMENT', session['permissions']):
    app.logger.info("Has Permission: True")
    if Admin.roleSave(jsonData):
      app.logger.info("Role Save:  True")
      content = render_template('roles_current.incl.jinja', roles=Admin.getRoles(),
                                                            roles_permissions=Admin.getRolesPermissions())
      retn = True  
      if not isinstance(content, str):
        content = content.decode('utf-8')

  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json'}


@app.route('/role/delete/<id>')
def role_delete(id):
  content = ''
  retn = False
  HttpCode = 200

  if not session.get('logged_in', False): return redirect("/")

  if Admin.checkPermission(session.get('user', None), 'PERMISSION_USER_MANAGEMENT', session['permissions']):
    if Admin.roleDelete(id):
      content = render_template('roles_current.incl.jinja', roles=Admin.getRoles(),
                                                            roles_permissions=Admin.getRolesPermissions())
      retn = True
      if not isinstance(content, str):
        content = content.decode('utf-8')
        
  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({ 'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json' }


# Task History

@app.route('/taskhistory/refresh')
def task_history_refresh():
  retn = False
  # Get the parsed contents of the form content
  jsonData = request.get_json()
  content = ''
  retn = False
  HttpCode = 200

  if not session.get('logged_in', False): return redirect("/")

  #app.logger.info("Role Save: {}".format(jsonData))

  if Admin.checkPermission(session.get('user', None), 'PERMISSION_AUTHENTICATED', session['permissions']):
      content = render_template('taskhistory_current.incl.jinja', task_history=TaskHistory.get())
      retn = True  
      if content and not isinstance(content, str):
        content = str(content.decode('utf-8'))

  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({'response': retn, 'content': content }), HttpCode, {'ContentType':'application/json'}


@app.route('/taskhistory/view/<id>')
def task_history_view(id):
  content = ''
  retn = False
  HttpCode = 200

  if not session.get('logged_in', False): return redirect("/")

  if Admin.checkPermission(session.get('user', None), 'PERMISSION_AUTHENTICATED', session['permissions']):
    taskHistoryItem = TaskHistory.getItem(id)
    title = TaskHistory.formatTitle(taskHistoryItem.task)
    content = render_template('taskhistory_detail.incl.jinja', task_history=taskHistoryItem)
    retn = True
    
    if content and not isinstance(content, str):
      content = str(content.decode('utf-8'))
        
  else:
    content = 'Not Authorized'
    HttpCode = 444

  return json.dumps({ 'response': retn, 'title': title, 'content': content }), HttpCode, {'ContentType':'application/json' }



# ------------------ redis Alert channel handlers --------------------

def get_sse_history():
  ''' '''
  sse_history = []
  key_pattern = app.config['CHANNEL_ALERT_KEY_PREFIX'] + '*'
  keys = _redis.keys(key_pattern)
  for key in keys:
    val = _redis.get(key)
    val = val.decode('utf-8').strip()
    sse_history.append(val)

  sse_history.sort()
  return sse_history


def get_log_history():
  ''' '''
  log_history = []
  key_pattern = app.config['CHANNEL_LOG_KEY_PREFIX'] + '*'
  keys = _redis.keys(key_pattern)
  keys.sort()
  for key in keys:
    val = _redis.get(key)
    val = val.decode('utf-8').strip()
    log_history.append(val)

  #log_history.sort()
  return log_history


# SSE (server sent message) handlers
def stream_channel():
  ''' '''
  channels = [
    app.config['CHANNEL_ALERT'],
    app.config['CHANNEL_LOG'],
    app.config['CHANNEL_QUEUE']
  ]
  pubsub = _redis.pubsub()
  pubsub.subscribe(channels)
  for message in pubsub.listen():
    print(message)
    yield "data: {}|||{}|||{}\n\n".format(message['channel'].decode('utf-8'), message['type'], str(message['data']))


@app.route('/stream')
def sse_stream():
  ''' '''
  resp = Response(stream_channel(), mimetype="text/event-stream")
  resp.headers['X-Accel-Buffering'] = 'no'
  return resp


#### debug for alerts ####

@app.route('/alert/send')
def alert_send():
  return render_template('send.html')


@app.route('/alert/push', methods=['POST'])
def alert_push():
    channels = [
      app.config['CHANNEL_ALERT'],
      app.config['CHANNEL_LOG']
    ]
    message = request.form['message']
    now = datetime.now().replace(microsecond=0).time()
    _redis.publish(channels, u'[%s] BigRedButton says: %s' % (now.isoformat(), message))
    resp = Response(status=202)
    resp.headers['X-Accel-Buffering'] = 'no'
    return resp




##############################

# handle session expiration
@app.before_request
def set_session_timeout():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=6)

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



@app.template_filter('timestamp')
def format_timestamp(d):
  ''' Jinja2 custom filter for formatting dates '''
  tz = pytz.timezone(app.config['TIMEZONE'])
  return datetime.fromtimestamp(int(d), tz).strftime('%Y-%m-%d %H:%M:%S')


@app.template_filter('nl2br')
def nl2br(content):
  ''' 
  Jinja2 custom filter for converting newlines to <br /> tags 
  also removes leading byte string coding, if present
  '''
  return Utils.trim(content)





