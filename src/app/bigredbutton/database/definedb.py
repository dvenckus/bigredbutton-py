#!/usr/bin/env python

#
# tabledef.py
#
# run this create & configure the brb.db database
#

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from user import *
from os import path
import sys
import getopt
from passlib.hash import sha256_crypt

########################################################################


def main():
  admin_user = ''
  admin_pswd = ''
  DATABASE_NAME = 'brb.db'

  # add 'echo=True' to turn on logging for create_engine
  engine = create_engine('sqlite:///' + DATABASE_NAME)

  # create tables
  Base.metadata.create_all(engine)

  # create a Session
  Session = sessionmaker(bind=engine)
  session = Session()
  session.commit()

  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["u=", "p="])
  except getopt.GetoptError:
    print 'Error:  missing arguments'
    usage()
    sys.exit('missing arguments')

  for a in args:
    if "u=" in a:
      tmp = a.split('=')
      admin_user = tmp[1]
    elif "p=" in a:
      tmp = a.split('=')
      admin_pswd = tmp[1]


  # add admin account
  if admin_user == '' or admin_pswd == '':
    print 'Error:  missing arguments'
    usage()
    sys.exit('missing admin username and password')

  password_enc = sha256_crypt.encrypt(admin_pswd)
  admin = session.query(User).filter_by(id=1).first()
  if admin is None:
    # create the admin user
    admin = User(admin_user, password_enc, "Admin")
    session.add(admin)
    print "Admin user (%s) created" % admin_user
  else:
    # update the admin user
    admin.username = admin_user
    admin.password = password_enc
    print "Admin user (%s) updated" % admin_user

  session.commit()

  print "Done!\n"



def usage():
  ''' Usage Statment '''
  # temporarily:  u=spinehealth p=brbpepperoni
  print "createdb.py u=[admin-username] p=[admin-pswd]"


# call the main function
#
if __name__ == "__main__":
  main()
