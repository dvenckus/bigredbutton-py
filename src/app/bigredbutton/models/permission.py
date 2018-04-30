#
# Class Permissions
#
from sqlalchemy import Column, Integer, String, Sequence
from models.meta import Base

########################################################################
class Permission(Base):
    """"""
    __tablename__ = "permissions"

    id = Column(Integer, Sequence('permission_id_seq'), primary_key=True)
    role_id = Column(Integer)
    permission = Column(String(50))

    #----------------------------------------------------------------------
    def __init__(self, role_id, permission):
        """"""
        self.role_id = role_id
        self.permission = permission

    def __repr__(self):
        return "<Permission(id='%d', role_id='%d', permission='%s')>" % (self.id, self.role_id, self.permission)
