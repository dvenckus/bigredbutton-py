  var sse_event = new EventSource("/stream");
  var out = document.getElementById('out');

  sse_event.addEventListener('open', function(e) { console.log('EventSource opened'); }, false);
  sse_event.addEventListener('error', function(e) { console.log('EventSource closed'); }, false);
  sse_event.addEventListener('message', function(e) {
                                          var json = JSON.parse(e);
                                          console.log(json);
                                          if (json.data.charAt(0) != '1') {
                                            out.innerHTML =  json.data + '<br />' + out.innerHTML;
                                          } else {
                                            out.innerHTML =  'subscribed to channel: ' + json.channel + '<br />' + out.innerHTML;
                                            window.subscribed = true
                                          }
                                        }, false);
