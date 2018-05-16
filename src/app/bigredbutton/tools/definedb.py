#!/usr/bin/env python3
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

def main():
  '''
  main
  this is an independent script not integrated with flask app
  sets up the database tables from the models
  configures the admin user/pass
  '''

  DATABASE_NAME = constants.SQLALCHEMY_DATABASE_URI

  # add 'echo=True' to turn on logging for create_enginebrb
  engine = create_engine(DATABASE_NAME)

  # create tables
  Base.metadata.create_all(engine)

  # create a Session
  Session = sessionmaker(bind=engine)
  session = Session()
  #session.commit()

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


  setup_admin_account(session, admin_user, admin_pswd)

  seed_roles(session)

  seed_permissions(session)

  seed_roles_permissions(session)

  print("Done!\n")


#
# function:  usage()
#
def usage():
  ''' Usage Statment '''
  # temporarily:  u=spinehealth p=brbpepperoni
  print("createdb.py u=[admin-username] p=[admin-pswd]")


#
# function:  setup_admin_account()
#
def setup_admin_account(session, admin_user='', admin_pswd=''):
  ''' create/update admin account '''
  try:
    # add admin account
    if admin_user == '' or admin_pswd == '':
      print('Error:  missing arguments')
      usage()
      sys.exit('missing admin username and password')

    

    password_enc = sha256_crypt.encrypt(admin_pswd)
    admin = session.query(User).filter_by(id=1).first()

    if admin is None:
      # create the admin user
      ROLE_ADMIN_ID = constants.ROLE_ADMIN
      ROLE_ADMIN_NAME = constants.ROLE_VALUES[constants.ROLE_ADMIN]
      admin = User(admin_user, password_enc, ROLE_ADMIN_NAME, ROLE_ADMIN_ID, 0)
      session.add(admin)
      print("Admin user (%s) created" % admin_user)
    else:
      # update the admin user
      admin.username = admin_user
      admin.password = password_enc
      print("Admin user (%s) updated" % admin_user)

    session.commit()
  except Exception as e:
    print('Error: ' + str(e))
    sys.exit(1)

#
# seed_roles
#
def seed_roles(session):
  ''' populate the role table '''
  try:

    row_count = session.query(Role).count()
    if not row_count:
      # table is empty, safe to populate
      role_list = []
      role_data = constants.ROLE_VALUES
      for id, name in role_data.items():
        role = Role(id, name)
        role_list.append(role)

      session.add_all(role_list)
      session.commit()

  except Exception as e:
    print('Seed Roles Error: ' + str(e))
    sys.exit(1)


#
# seed_permissions
#
def seed_permissions(session):
  ''' populate the permissions table '''
  try:
    row_count = session.query(Permission).count()
    if not row_count:
      # table is empty, safe to populate
      permission_list = []
      permission_data = constants.PERMISSION_VALUES
      for id, name in permission_data.items():
        permission = Permission(id, name)
        permission_list.append(permission)

      session.add_all(permission_list)
      session.commit()

  except Exception as e:
    print('Seed Permissions Error: ' + str(e))
    sys.exit(1)

#
# seed_role_permissions
#
def seed_roles_permissions(session):
  ''' populate the permissions table '''
  try:
    row_count = session.query(RolePermission).count()
    if not row_count:
      # table is empty, safe to populate
      permission_list = []
      permission_data = constants.ROLE_PERMISSION_VALUES
      for role_id, permissions in permission_data.items():
        for permission_id in permissions:
          permission = RolePermission(role_id, permission_id)
          permission_list.append(permission)

      session.add_all(permission_list)
      session.commit()

  except Exception as e:
    print('Seed Roles Permissions Error: ' + str(e))
    sys.exit(1)



# call the main function
#
if __name__ == "__main__":
  if __package__ is None:
    app_path = path.dirname(path.dirname(path.abspath(__file__)))
    src_dir = path.dirname(path.dirname(app_path))
    sys.path.append(app_path)
    sys.path.append(src_dir)
    from models.meta import Base
    from models.role import Role
    from models.permission import Permission
    from models.rolepermission import RolePermission
    from models.user import User
    from models.taskitem import TaskItem
    from models.taskhistory import TaskHistory
    import constants

    #print("SQLALCHEMY_DATABASE_URI: {}".format(constants.SQLALCHEMY_DATABASE_URI))
    #print("PATH: {}".format(sys.path))

  main()
