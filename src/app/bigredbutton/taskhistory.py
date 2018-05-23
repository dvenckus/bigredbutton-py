#
# taskhistory.py
#
from app.bigredbutton import app, db
#from models.meta import Base
from models.taskhistoryitem import TaskHistoryItem
from tasks import TasksList
from sqlalchemy import exc, desc
import os
from utils import Utils


class TaskHistory(object):

  ''' limit of history to the last n tasks '''
  MAX_HISTORY = 100

  @staticmethod
  def get():
    ''' return records from the task_history table '''
    history = None
    doCommit = False
    
    try: 
      # retrieve the history table
      history = db.session.query(TaskHistoryItem).order_by(desc(TaskHistoryItem.timestamp)).all()

      for idx, item in enumerate(history):
        if idx < TaskHistory.MAX_HISTORY:
          # only retain the last ~100 tasks run
          if len(history[idx].result) > 50:
            # don't display the entire result... too long
            if history[idx].result and not isinstance(history[idx].result, str):
              history[idx].result = history[idx].result.decode('utf-8')
            history[idx].result = '...' + history[idx].result[-50:]
            pos = history[idx].result.find("Completed [")
            if pos: history[idx].result = history[idx].result[pos:].strip()
            # history[idx].result = "<br />".join(history[idx].result.strip().split("\n"))
        else:
          # trim the excess history
          db.session.delete(history[idx])
          doCommit = True
        idx += 1

      if doCommit:
        db.session.commit()

    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error(str(e))

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
    
    title = taskListItem['name']
    return title
  

