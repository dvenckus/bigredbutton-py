#
# tools.py
#

class Tools(object):

  @staticmethod
  def formatAttributes(attributes):
    '''
    converts dictionary of attributes into formatted string for
    including with html elements
    '''
    f_attrib = ''

    if not attributes:
      return f_attrib

    for name, value in attributes:
      f_attrib += '%s %s="%s"' % (f_attrib, name, value)

    return f_attrib
