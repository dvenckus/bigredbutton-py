  //server-sent-events handler
  var sse_event = new EventSource("/stream");
  var out = $('#sse-out');

  function convString(str) {
    if (str[0] == 'b') {
      return str.substring(2, str.length-1)
    }
    return str
  }

  sse_event.addEventListener('open', function(e) { console.log('EventSource opened'); }, false);
  sse_event.addEventListener('error', function(e) { console.log('EventSource closed'); }, false);
  sse_event.addEventListener('message', function(e) {
                                          console.log(e.data);
                                          var fields = e.data.split('|');
                                          var channel = String(fields[0]);
                                          var type = fields[1];
                                          var message = convString(fields[2]);
                                          if (type != 'subscribe') {
                                            out.html(message + '<br />' + out.html());
                                            if (message.indexOf("END TASK") !== -1) {
                                              window.getQueue();
                                            }
                                          } else {
                                            if (window.subscribed != true) {
                                              out.html(channel + ' enabled<br />' + out.html());
                                              window.subscribed = true;
                                            }
                                          }
                                        }, false);
