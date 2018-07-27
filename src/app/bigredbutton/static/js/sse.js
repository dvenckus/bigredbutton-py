$(document).ready(function() {
  
  /*
  window.scrollDown = function() {
    //$('#output').prop("scrollHeight") - $('#output').height()
    $('#output').animate({scrollTop: $('#output').prop("scrollHeight")}, 500);
  };
  */
  
  window.appendOutput = function(content) {
    var $logstream = $('#output');
    if ($logstream.text().length) {
      content = '<br/>' + content;
    }
    $logstream.append(content)
                  .delay(500)
                  .fadeIn({
                    duration: 500,
                    start: $logstream.animate({scrollTop: $('#output').prop("scrollHeight")}, 500)
                  });
  };


  //server-sent-events handler
  var sse_event = new EventSource("/stream");
  var $alerts = $('#sse-out');
  var $queue = $('#queue-body');


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
    var fields = e.data.split('|||');
    var channel = String(fields[0]);
    var type = fields[1];
    var message = convString(fields[2]);
    if (channel == 'queue') {
      if ((type != 'subscribe') && (message != '')) {
        $queue.html(message);
      }
    } else if (channel == 'alerts') {
      if (type != 'subscribe') {
        $alerts.prepend(message + '<br />');
        if (message.indexOf("END TASK") !== -1) {
          //window.getQueue();
          // find the ID tag from the message
          var pattern = /\[ID\=([0-9]+)\]$/g;
          var result = pattern.exec(message);
          console.log('END TASK id match: ' + result);
          if (typeof result[1] !== 'undefined') {
            var taskid = result[1];
            // remove from queue
            $('#task-' + taskid).remove();
            // if queue is empty, add the 'Empty' row
            if ($('#queue tbody tr').length == 0) {
              $queue.html('<tr id="task-0" class="empty"><td colspan="7">EMPTY</td></tr>');
            }
           
          }
        } 
      } else {
        if (window.subscribed_alerts != true) {
          $alerts.prepend(channel + ' enabled<br />');
          window.subscribed_alerts = true;
        }
      }
    } else if (channel == 'logstream') {
      if ((type != 'subscribe') && (message != '')) {
        window.appendOutput(message);
      } else {
        if (window.subscribed_logstream != true) {
          window.appendOutput(channel + ' enabled');
          window.subscribed_logstream = true;
        }
      }
    }
  }, false);

});
