#
# utils.py
#
#from app.bigredbutton import app
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

    # strip whitespace - for longish strings regex works best here
    content = re.sub(r'^\s+', "", content)
    #app.logger.info("Utils::trim() rstrip/strip: " + str(content))

    # convert newlines to html breaks
    # content = re.sub("\\\\n", "<br />", content)
    # content = re.sub("\\\\r", "", content)
    
    #content = re.sub("\\\\\\r", "", content)
    content = re.sub("\n", "<br />", content)
    content = re.sub("\r", "", content)
    content = re.sub("\\\"", "", content)
    
    #app.logger.info("Utils::trim() newlines to breaks: " + str(content))
    return content.strip()


  #
  # parseTaskResult()
  #
  @staticmethod
  def parseTaskResult(full_output=''):
    ''' '''
    result = full_output

    if len(result) > 50:
      # don't disprvice lay the entire result... too long
      if result and not isinstance(result, str):
        result = str(result.decode('utf-8'))
      # trim down to last 50 chars
      result = result[-50:]
      m = re.search('(Completed [\[A-Z]+\])', result)
      if m and m.group(0):
        result = m.group(0)
      else:
        result = '...' + result

    return result