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
    name = Column(String(50))

    #----------------------------------------------------------------------
    def __init__(self, id, name):
        """"""
        if id:
          self.id = id
        self.name = name

    def __repr__(self):
        return "<Permission(id='{}', name='{}')>".format(self.id, self.name)

    def toDict(self):
      dict_ = {}
      for key in self.__mapper__.c.keys():
          dict_[key] = getattr(self, key)
      return dict_
