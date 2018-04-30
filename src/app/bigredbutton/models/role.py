#
# Class Role
#
from sqlalchemy import Column, Integer, String, Sequence
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
        return "<Role(id='%d', name='%s')>" % (self.id, self.name)
