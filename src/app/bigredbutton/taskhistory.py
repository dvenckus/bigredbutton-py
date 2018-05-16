#
# taskhistory.py
#
from app.bigredbutton import app, db
from models.meta import Base
from models.taskhistoryitem import TaskHistoryItem
from sqlalchemy import exc, desc
import os


class TaskHistory(object):

  ''' limit of history to the last n tasks '''
  MAX_HISTORY = 100

  @staticmethod
  def get():
    ''' return records from the task_history table '''
    history = None

    try:
      # retrieve the history table
      history = db.session.query(TaskHistoryItem).order_by(desc(TaskHistoryItem.timestamp)).all()

      # trim the excess history
      if history and len(history) > TaskHistory.MAX_HISTORY:
        index = TaskHistory.MAX_HISTORY
        while history[index]:
          db.session.delete(history[index])
          index += 1

        db.session.commit()

    except exc.SQLAlchemyError as e:
      app.logger.error(str(e))
    except Exception as e:
      app.logger.error(str(e))

    return history