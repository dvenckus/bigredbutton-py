#
# Admin.py
#
from flask import Flask, session
from sqlalchemy import exc
from app.bigredbutton import app, db
#from models.meta import Base
from models.user import User
from models.permission import Permission
from models.role import Role
from models.rolepermission import RolePermission
from passlib.hash import sha256_crypt
import logging


class Admin(object):

  @staticmethod
  def validateUser(input_username='', input_password=''):
    ''' 
    validate the username and password to begin the session 
    retrieves the user permissions
    sets 'valid' as True|False if user is valid
    returns a dictionary

    Note:  cannot use Session object in this class, session object can only be referenced from 
    a request handler
    '''
    try:
      userSession = { 'valid': False }

      if input_username == '' or input_password == '':
        app.logger.info('Missing Login Input: {}, {}'.format(input_username, input_password))
        return userSession

      # retrieve the user record
      user = db.session.query(User).filter_by(username=input_username).first()

      password_enc = sha256_crypt.encrypt(input_username)

      app.logger.info("user found: {}".format(str(user)))
      app.logger.info("match passwords...")
      app.logger.info("  user entered:  {}".format(password_enc))
      app.logger.info("  user existing: {}".format(user.password))              

      if user.password and sha256_crypt.verify(input_password, str(user.password)):
        app.logger.info('User Password is valid')
        permission_list = Admin.getRolePermissions(role_id=user.role_id, id_list=True)

        if Admin.checkPermission(user, 'PERMISSION_AUTHENTICATED', permission_list):
          # valid user and correct permission
          app.logger.info('User has Authenticated permission')
          userSession['valid'] = True
          userSession['user'] = user
          userSession['permissions'] = permission_list
      #else:
      #  app.logger.info('User Password is invalid')
        

      return userSession
    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error(str(e))


  
  @staticmethod
  def checkPermission(user=None, permission='', permissions=[]):
    ''' checks the permission and returns True|False accordingly '''
    if user:
      # check type here, could be Users class or plain ol' dict 
      if type(user) == type(dict()):
        user_role_id = user['role_id']
      else:
        user_role_id = user.role_id

      if user_role_id == app.config['ROLE_ADMIN']: 
        # admin role, automatically has ALL permissions
        return True

    permission_id = app.config.get(permission, 0)
    #app.logger.info("checkPermission: {}({})".format(permission, permission_id))
    #app.logger.info("permissions: {}".format(str(permissions)))
    if not permission_id or not permissions: return False
    return (permission_id in permissions)


  @staticmethod
  def getUsers():
    '''
    Wrapper for getUser()
    '''
    return Admin.getUser()


  @staticmethod
  def getUser(uid=0):
    '''
    Retrieves all users from the users table 
    returns a dictionary
    '''
    try:
      # retrieve the users table
      if uid:
        user = db.session.query(User).filter_by(id=uid).first()
        return user
      

      users = db.session.query(User).all()
      return users
          
    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error(str(e))


  @staticmethod
  def userSave(updated_by, data):
    ''' 
    add user 
    logs the user id of the current user creating the new user record
    '''
    try:
      user_id = int(data['user_id']) if data['user_id'] != '' else 0

      if not user_id:
        # adding new user
        password_enc = sha256_crypt.encrypt(data['password'])
        new_user = User(username=data['username'], password=password_enc, realname=data['realname'], role_id=int(data['role_id']), updated_by=updated_by)
        db.session.add(new_user)
      else:
        # editing existing user
        user = Admin.getUser(data['user_id'])
        user.realname = data['realname']
        user.username = data['username']
        user.role_id = data['role_id']
        user.updated_by = updated_by

        if data['password']:
          # updating password
          password_enc = sha256_crypt.encrypt(data['password'])
          user.password = password_enc

        db.session.add(user)

      db.session.commit()
      return True

    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error(str(e))

    return False


  @staticmethod
  def userDelete(id):
    ''' delete user '''
    try:
      user = Admin.getUser(id)
      if user:
        db.session.delete(user)
        db.session.commit()
        return True
    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
      db.session.rollback()
    except Exception as e:
      app.logger.error(str(e))

    return False


  @staticmethod
  def getRoles():
    '''
    Wrapper for getRole()
    '''
    return Admin.getRole()



  @staticmethod
  def getRole(rid=0):
    '''
    Retrieves the individual Role if an rid parameter is provided, otherwise
    Retrieves all roles from the roles table 
    '''
    roles = None
    try:
      if rid:
        return db.session.query(Role).filter_by(id=rid).first()

      # retrieve the roles table
      roles = db.session.query(Role).all()
          
    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error(str(e))

    return roles



  @staticmethod
  def roleSave(data):
    ''' 
    add/update role 
    '''
    try:

      app.logger.info("Admin.roleSave()")

      role_id = int(data['role_id']) if data['role_id'] != '' else 0

      app.logger.info("RoleId: {}".format(role_id))

      permission_list = []
      input_permission_list = [ int(x) for x in data['role_permissions'] ]

      auth_permission = app.config['PERMISSION_AUTHENTICATED']
      if auth_permission not in input_permission_list:
        # add authenticated to the permission list
        input_permission_list.append(auth_permission)


      if not role_id:
        # adding new user
        new_role = Role(name=data['role_name'])
        db.session.add(new_role)

        db.session.flush()
        db.session.refresh(new_role)
        app.logger.info("New Role: {}".format(str(new_role)))
        role_id = new_role.id

        new_permission_list = []

        for permission_id in input_permission_list:
          new_permission = RolePermission(role_id=role_id, permission_id=permission_id)
          new_permission_list.append(new_permission)

        app.logger.info("Role Permissions [selected]: {}".format(str(input_permission_list)))
          
        db.session.add_all(new_permission_list)
          
      else:
        # editing existing role
        role = Admin.getRole(role_id)
        role.name = data['role_name']
        db.session.add(role)

        if not role:
          app.logger.info("Role not found")
          return False

        # get existing role permissions
        existing_permissions_list = Admin.getRolePermissions(role_id=role_id, id_list=True)

        app.logger.info("Role: {}".format(str(role)))
        app.logger.info("Role Permissions [original]: {}".format(str(existing_permissions_list)))
        app.logger.info("Role Permissions [selected]: {}".format(str(input_permission_list)))
        

        add_list = []
        delete_list = []
        if set(input_permission_list) != set(existing_permissions_list):
          add_list = list(set(input_permission_list) - set(existing_permissions_list))
          delete_list = list(set(existing_permissions_list) - set(input_permission_list))
          app.logger.info("rolePermissions do not match")
        else:
          app.logger.info("rolePermissions match")

        app.logger.info("Adding new permissions: {}".format(str(add_list)))
        app.logger.info("Deleting unselected permissions: {}".format(str(delete_list)))

        if add_list:
          new_permission_list = []
          for permission_id in add_list:
            new_permission = RolePermission(role_id=role_id, permission_id=permission_id)
            new_permission_list.append(new_permission)

          # add the new permissions selected
          db.session.add_all(new_permission_list)

        if delete_list:
          # remove the permissions no longer selected
          for rolePermission in db.session.query(RolePermission).filter_by(role_id=role_id).all():
            if rolePermission.permission_id in delete_list:
              db.session.delete(rolePermission)
          
          
      db.session.commit()
      db.session.flush()
        

      ## debug only ##
      permission_list = Admin.getRolePermissions(role_id=role_id, id_list=True)
      app.logger.info("Updated RolePermissions list: {}".format(str(permission_list)))

      return True

    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
      db.session.rollback()
    except Exception as e:
      app.logger.error(str(e))

    return False



  @staticmethod
  def roleDelete(id):
    ''' delete role '''
    try:
      if not id: return False

      # are there existing users with this role?
      if db.session.query(User).filter_by(role_id=id).count():
        app.logger.info("Unable to delete a Role assigned to a User")
        return False

      for rolePermission in db.session.query(RolePermission).filter_by(role_id=id).all():
        db.session.delete(rolePermission)

      role = db.session.query(Role).filter_by(id=id).first()
      db.session.delete(role)

      db.session.commit()
      return True

    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
      db.session.rollback()
    except Exception as e:
      app.logger.error(str(e))

    return False



  @staticmethod
  def getPermissions():
    '''
    Returns all permissions from the Permissions table
    '''
    try:
      # retrieve the users table
      permissions = db.session.query(Permission).all()
      return permissions
          
    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error(str(e))




  @staticmethod
  def getRolesPermissions():
    '''
    Wrapper for getRolePermissions()
    '''
    return Admin.getRolePermissions()



  @staticmethod
  def getRolePermissions(role_id=0, id_list=False):
    '''
    Retrieves permission_id list or full record for a single role
    '''
    try:
      permission_list = []     
      rolesPermissions = None 

      if role_id: 
        rolesPermissions = db.session.query(RolePermission).filter_by(role_id=role_id).all()
      else:
        rolesPermissions = db.session.query(RolePermission).all()

      if id_list:
        for rp in rolesPermissions:
          permission_list.append(rp.permission_id)
        return permission_list

      return rolesPermissions

    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error(str(e))



  
