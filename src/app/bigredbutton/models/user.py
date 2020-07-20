#
# Class User
#
from sqlalchemy import Column, Integer, SmallInteger, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.meta import Base
from models.unixtimestamp import UnixTimestamp

########################################################################
class User(Base):
    """"""
    __tablename__ = "users"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(25), unique=True)
    password = Column(String(100))
    realname = Column(String(25), unique=True)
    role_id = Column(SmallInteger, ForeignKey('roles.id'))
    role = relationship("Role", uselist=False, backref="users")
    updated = Column(UnixTimestamp)
    updated_by = Column(Integer)

    

    #----------------------------------------------------------------------
    def __init__(self, username, password, realname, role_id, updated_by):
        """"""
        self.username = username
        self.password = password
        self.realname = realname
        self.role_id = role_id
        self.updated_by = updated_by   #user id


    def __repr__(self):
        return "<User(id='%d', username='%s', password='xxxxxxx', realname='%s', role_id='%d', role='%s', updated='%s', updated_by='%d')>" % (
                      self.id, self.username, self.password, self.realname, self.role_id, str(self.role), self.updated, self.updated_by)

    def toDict(self):
      dict_ = {}
      for key in self.__mapper__.c.keys():
          dict_[key] = getattr(self, key)
      return dict_

