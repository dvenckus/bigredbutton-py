//server-sent-events handler
var sse_event = new EventSource("/stream");
var alerts = $('#sse-out');
var logstream = $('#output');

function convString(str) {
  if (str[0] == 'b') {
    return str.substring(2, str.length-1);
  }
  return str.trim();
}

sse_event.addEventListener('open', function(e) { console.log('EventSource opened'); }, false);
sse_event.addEventListener('error', function(e) { console.log('EventSource closed'); }, false);
sse_event.addEventListener('message', function(e) {
  console.log(e.data);
  var fields = e.data.split('|');
  var channel = String(fields[0]);
  var type = fields[1];
  var message = convString(fields[2]);
  if (channel == 'alerts') {
    if (type != 'subscribe') {
      alerts.prepend(message + '<br />');
      if (message.indexOf("END TASK") !== -1) {
        window.getQueue();
      } 
    } else {
      if (window.subscribed_alerts != true) {
        alerts.prepend(channel + ' enabled<br />');
        window.subscribed_alerts = true;
      }
    }
  } else if (channel == 'logstream') {
    if (logstream.text().length) {
      logstream.append('<br/>');
    }
    if ((type != 'subscribe') && (message != '')) {
      logstream.append(message);
    } else {
      if (window.subscribed_logstream != true) {
        logstream.append(channel + ' enabled');
        window.subscribed_logstream = true;
      }
    }
  }
}, false);
