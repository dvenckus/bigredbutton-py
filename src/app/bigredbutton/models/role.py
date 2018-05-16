#
# Class Role
#
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.meta import Base

########################################################################
class Role(Base):
    """"""
    __tablename__ = "roles"

    id = Column(Integer, Sequence('role_id_seq'), primary_key=True)
    name = Column(String(25), unique=True)


    #----------------------------------------------------------------------
    def __init__(self, id=None, name=''):
        """"""
        if id:
          self.id = id
        self.name = name

    def __repr__(self):
        return "<Role(id='{}', name='{}')>".format(self.id, self.name)

    def toDict(self):
      dict_ = {}
      for key in self.__mapper__.c.keys():
          dict_[key] = getattr(self, key)
      return dict_
