#
# utils.py
#

class Utils(object):

  def trim(content):
    ''' '''
    # decode the content
    if content and not isinstance(content, str):
      content = str(content.decode('utf-8'))

    # clean up
    if content.startswith("b'"):
      content = content.strip("b'")

    # strip whitespace
    content = content.strip("\n")

    # convert newlines to html breaks
    content = "<br />".join(content.split("\n"))
    return content