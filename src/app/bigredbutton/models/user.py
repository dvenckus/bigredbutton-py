#
# Class User
#
from sqlalchemy import Column, Integer, String
from models.meta import Base

########################################################################
class User(Base):
    """"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    password = Column(String(100))
    realname = Column(String(25), unique=True)

    #----------------------------------------------------------------------
    def __init__(self, username, password, realname):
        """"""
        self.username = username
        self.password = password
        self.realname = realname

    def __repr__(self):
        return "<User(id='%d', username='%s', password='%s', realname='%s')>" % (
                      self.id, self.username, self.password, self.realname)
