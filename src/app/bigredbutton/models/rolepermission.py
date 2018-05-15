#
# Class RolePermission
#
from sqlalchemy import Column, Integer, SmallInteger, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.meta import Base

########################################################################
class RolePermission(Base):
    """"""
    __tablename__ = "roles_permissions"

    id = Column(Integer, Sequence('role_permission_id_seq'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship("Role", uselist=False, backref="roles_permissions")
    permission_id = Column(Integer, ForeignKey('permissions.id'))
    permission = relationship("Permission")

    #----------------------------------------------------------------------
    def __init__(self, role_id, permission_id):
        '''  '''
        self.role_id = role_id
        self.permission_id = permission_id

    def __repr__(self):
        return "<RolePermission(id='{}', role_id='{}', role='{}', permission_id='{}', permission='{}')>".format(
                self.id, self.role_id, str(self.role), self.permission_id, str(self.permission))

    def toDict(self):
      dict_ = {}
      for key in self.__mapper__.c.keys():
          dict_[key] = getattr(self, key)
      return dict_