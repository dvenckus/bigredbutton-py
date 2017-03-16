#!/usr/bin/env python
#
# tabledef.py
#
# run this create & configure the brb.db database
#
import datetime
import getopt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import sys, path
from passlib.hash import sha256_crypt

########################################################################

app_path = ''

def main():
  '''
  main
  this is an independent script not integrated with flask app
  sets up the database tables from the models
  configures the admin user/pass
  '''

  DATABASE_NAME = app_path + '/database/brb.db'

  # add 'echo=True' to turn on logging for create_engine
  engine = create_engine('sqlite:///' + DATABASE_NAME)

  # create tables
  Base.metadata.create_all(engine)

  # create a Session
  Session = sessionmaker(bind=engine)
  session = Session()
  session.commit()

  admin_user = ''
  admin_pswd = ''

  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["u=", "p="])
  except getopt.GetoptError as e:
    print('Error:  missing arguments')
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
    print('Error:  missing arguments')
    usage()
    sys.exit('missing admin username and password')

  password_enc = sha256_crypt.encrypt(admin_pswd)
  admin = session.query(User).filter_by(id=1).first()
  if admin is None:
    # create the admin user
    admin = User(admin_user, password_enc, "Admin")
    session.add(admin)
    print("Admin user (%s) created" % admin_user)
  else:
    # update the admin user
    admin.username = admin_user
    admin.password = password_enc
    print("Admin user (%s) updated" % admin_user)

  session.commit()

  print("Done!\n")



def usage():
  ''' Usage Statment '''
  # temporarily:  u=spinehealth p=brbpepperoni
  print("createdb.py u=[admin-username] p=[admin-pswd]")


# call the main function
#
if __name__ == "__main__":
  if __package__ is None:
    app_path = path.dirname(path.dirname(path.abspath(__file__)))
    sys.path.append(app_path)
    from models.meta import Base
    from models.user import User
    from models.taskitem import TaskItem

  main()
