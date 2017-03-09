  //server-sent-events handler
  var sse_event = new EventSource("/stream");
  var out = $('#sse-out');

  sse_event.addEventListener('open', function(e) { console.log('EventSource opened'); }, false);
  sse_event.addEventListener('error', function(e) { console.log('EventSource closed'); }, false);
  sse_event.addEventListener('message', function(e) {
                                          console.log(e.data);
                                          var fields = e.data.split('|');
                                          var channel = String(fields[0]);
                                          var type = fields[1];
                                          var message = fields[2];
                                          if (type != 'subscribe') {
                                            out.html(message + '<br />' + out.html());
                                            if (message.indexOf("Task Ended") !== -1) {
                                              window.getQueue();
                                            }
                                          } else {
                                            if (window.subscribed != true) {
                                              out.html(channel + ' enabled<br />' + out.html());
                                              window.subscribed = true;
                                            }
                                          }
                                        }, false);
