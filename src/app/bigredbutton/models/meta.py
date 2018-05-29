from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()

#
# SimpleObject - experimental, didn't quite work
#
# class SimpleObject(object):
#   ''' utility class for converting json data to python object '''
#   def __init__(self, _dict):
#     self.__dict__.update(_dict)
  # def toDict(self):
  #   ''' convert object to dict '''
  #   dict_ = {}
  #   for key in __dict__keys():
  #     dict_[key] = getattr(self, key)
  #   return dict_


#
# BaseItem
#
class BaseItem(object):
  '''
  Base class for PushItem, TaskItem, and TaskHistoryItem
  '''
  options = ''
  parsedOptions = {}

  def toDict(self):
    ''' convert object to dict '''
    dict_ = {}
    for key in self.__mapper__.c.keys():
        dict_[key] = getattr(self, key)
    return dict_


  def parseOptions(self):
    ''' 
    parse options string into json dict 
    call json.loads 2x to handle improperly quoted strings; 
    1st call converts to json-compatible string
    2nd call, if necessary, converts to json dict
    '''
    #self.parsedOptions = json.loads(json.loads(self.options))
    json_obj = json.loads(self.options)
    if isinstance(json_obj, str):
      # problem with json, call loads again
      json_obj = json.loads(json_obj)
      
    self.parsedOptions = json_obj
    return self.parsedOptions



