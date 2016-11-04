#!/usr/bin/env python
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.hash import sha256_crypt
import getopt
import sys
from user import *

def main():
  ''' main '''

  DATABASE_NAME = 'brb.db'

  admin_user = ''
  admin_pswd = ''
  uid = 0
  username = ''
  password = ''
  realname = ''

  action = ''
  ACTION_ADD = 'ADD'
  ACTION_UPDATE = 'UPD'
  ACTION_DELETE = 'DEL'
  ACTION_LIST = 'LIST'

  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["u=", "p=", "--add", "--update", "--delete", "--list", "id=", "username=", "password=", "realname="])
  except getopt.GetoptError:
    print 'Error:  missing arguments'
    usage()
    sys.exit('exiting')

  for a in args:
    if "u=" in a:
      tmp = a.split('=')
      admin_user = tmp[1]
    elif "p=" in a:
      tmp = a.split('=')
      admin_pswd = tmp[1]
    elif a == "--add":
      if action == '': action = ACTION_ADD
    elif a == "--update":
      if action == '': action = ACTION_UPDATE
    elif a == "--delete":
      if action == '': action = ACTION_DELETE
    elif a == "--list":
      if action == '': action = ACTION_LIST
    elif "id=" in a:
      tmp = a.split('=')
      uid = tmp[1]
    elif "username=" in a:
      tmp = a.split('=')
      username = tmp[1]
    elif "password=" in a:
      tmp = a.split('=')
      password = tmp[1]
    elif "realname=" in a:
      tmp = a.split('=')
      realname = tmp[1]

  # check for admin credentials
  if admin_user == '' or admin_pswd == '':
    print "Missing admin credentials [u], [p]\n"
    usage()
    sys.exit('exiting')

  # add 'echo=True' to turn on logging for create_engine
  engine = create_engine('sqlite:///' + DATABASE_NAME)

  # create a Session
  Session = sessionmaker(bind=engine)
  session = Session()

  try:
    # verify admin
    admin = session.query(User).filter_by(id=1).first()
    if admin is None:
      print "Error:  Unable to find admin account"
      sys.exit('exiting')

    #password_enc = sha256_crypt.encrypt(admin_pswd)
    if not sha256_crypt.verify(admin_pswd, str(admin.password)):
      print "Admin password invalid"
      sys.exit('exiting')

  except Exception,e:
    print "Error: ", e
    sys.exit('invalid login')


  try:
    # add / update / delete user

    if ACTION_LIST == action:
      users = session.query(User).all()

      print "\n"
      print "%s | %s | %s" % ( 'Id'.rjust(4), 'Realname'.ljust(25), 'Username'.ljust(25) )
      print "%s-|-%s-|-%s" % ('-' * 4, '-' * 25, '-' * 25)
      if len(users):
        for user in users:
          print "%s | %s | %s" % (str(user.id).rjust(4), user.realname.ljust(25), user.username.ljust(25))
      else:
        print "None"

      print "\n\n"

    elif ACTION_ADD == action:
      # check if the user already exists
      user = session.query(User).filter_by(username=username).first()
      if user:
        print "User %s already exits" % username
        sys.exit('exiting')

      # create the new user
      password_enc = sha256_crypt.encrypt(password)
      user = User(username, password_enc, realname)
      session.add(user)
      session.commit()
      print "User (%s) added" % username

    elif ACTION_UPDATE == action:
      user = None
      if uid > 0:
        user = session.query(User).filter_by(id=uid).first()
      else:
        user = session.query(User).filter_by(username=username).first()

      if not user:
        print "Unable to update.  User %s not found." % username
        sys.exit('exiting')

      if uid > 0 and username != user.username:
        user.username = username

      if password != '':
        user.password = sha256_crypt.encrypt(password)

      if realname != '':
        user.realname = realname

      session.commit()
      print "User (%s) updated" % username

    elif ACTION_DELETE == action:
      if uid > 0:
        delete = session.query(User).filter_by(id=uid).delete()
      else:
        delete = session.query(User).filter_by(username=username).delete()

      session.commit()
      print "User (%s) deleted" % username




  except Exception,e:
    print "Error: ", e
    sys.exit('exiting')


  # wrap it up

  # commit the record the database
  #session.commit()

  #session.commit()

  print "Done!\n"



  # ----- end - main() -----


#
# usage statement
#
def usage():
  ''' Usage Statment '''
  print "List Users:"
  print "brbadmin.py u=[admin-username] p=[admin-pswd] --list\n"
  print "Add User:"
  print "brbadmin.py u=[admin-username] p=[admin-pswd] --add username=[username] password=[password] realname=[real name]\n"
  print "Update User:"
  print "brbadmin.py u=[admin-username] p=[admin-pswd] --update username=[username] password=[password] realname=[real name]\n"
  print "Delete User:"
  print "brbadmin.py u=[admin-username] p=[admin-pswd] --delete username=[username]\n"


#
# call the main function
#
if __name__ == "__main__":
  main()
