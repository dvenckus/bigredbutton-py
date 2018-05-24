#
# utils.py
#
from app.bigredbutton import app
import re



class Utils(object):

  @staticmethod
  def trim(content):
    ''' '''
    #app.logger.info("Utils::trim() raw: " + str(content))

    # decode the content
    if content and not isinstance(content, str):
      content = str(content.decode('utf-8'))

    #app.logger.info("Utils::trim() decoded: " + str(content))

    # clean up
    if content.startswith("b'"):
      content = content.lstrip('b').strip("'")
    #app.logger.info("Utils::trim() strip b': " + str(content))

    # strip whitespace
    content = content.strip('\n')
    #app.logger.info("Utils::trim() rstrip/strip: " + str(content))

    # convert newlines to html breaks
    content = re.sub(r'\\n', '<br />', content)
    #app.logger.info("Utils::trim() newlines to breaks: " + str(content))
    return content