#
# taskhistory.py
#
from app.bigredbutton import app, db
#from models.meta import Base
from models.taskhistoryitem import TaskHistoryItem
from tasks import TasksList
from sqlalchemy import exc, desc
from utils import Utils
import re
import sys

class TaskHistory(object):

  ''' limit of history to the last n tasks '''
  MAX_HISTORY = app.config['MAX_TASK_HISTORY']

  @staticmethod
  def get():
    ''' return records from the task_history table '''
    history = None
    doCommit = False
    
    try: 
      # retrieve the history table
      history = db.session.query(TaskHistoryItem).order_by(desc(TaskHistoryItem.timestamp)).all()

      for idx, item in reversed(list(enumerate(history))):
        if idx >= TaskHistory.MAX_HISTORY:
          # trim the excess history
          db.session.delete(history[idx])
          doCommit = True
        else:
          break
        idx += 1

      if doCommit:
        db.session.commit()

    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
      app.logger.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    except Exception as e:
      app.logger.error(str(e))
      app.logger.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))

    return history


  @staticmethod
  def getItem(id):
    ''' retrieve a specific TaskHistoryItem '''
    historyItem = None
    try:
       # retrieve the history table
      historyItem = db.session.query(TaskHistoryItem).filter_by(id=id).first()

      historyItem.result = Utils.trim(historyItem.result)

    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error(str(e))

    return historyItem


  @staticmethod
  def formatTitle(task):
    ''' '''
    title = ''

    if not task: return title

    taskListItem = TasksList.getListItem(task)
    if not TasksList: return title
    
    try:
      title = taskListItem['name']
    except KeyError:
      title = 'Task Unknown'
    return title
  

