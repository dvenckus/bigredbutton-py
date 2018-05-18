/*
*   javascript: preprod.js
*/
$(document).ready(function() {
  
  // Pre-Production ----------------------------------------

  function clearFormPreProd() {
    $('#subdomains-preprod').val(0);
    $('#sites-preprod').val(0);
    $('#tasks-preprod').val(0);
    $('#chk-backup-database-preprod').prop('checked', false);
  };

  $('#clearFormPreProd').click(function() {
    clearFormPreProd();
  });

  
  clearFormPreProd();


  function updateQueue(data) {
    // updates the queue display with the current items
    if (data.response == true) {
      //console.log('updateQueue: ' + data.content)
      $("#queue tbody").html(data.content);
      clearFormPreProd();
    }
    window.queueBusy = false
  };


  window.getQueue = function() {
    if (window.queueBusy == true) { return; }
    window.queueBusy = true

    $.ajax({
      type: "GET",
      url: "/queue",
      //contentType: 'application/json',
      data: '',
      dataType: 'json',
      success: updateQueue
    });
  };


  $('#btnQueuePreprod').click(function() {
    var subdomain = $('#subdomains-preprod').val();
    var site = $('#sites-preprod').val();
    var task = $('#tasks-preprod').val();

    if (subdomain == '-' || subdomain == '0' ||
        site == '-' || site == '0' ||
        task == '-' || task == '0') {
      alert('Invalid selection');
      return false;
    }

    var dbbackup = $('#chk-backup-database-preprod').prop('checked') ? 1 : 0;
    var sitelist = [];

    if (site == 'all') {
      $('#sites-preprod option.site').each(function() {
        sitelist.push(this.value);
      });
    } else if (site == 'hlth') {
      $('#sites-preprod option.health').each(function() {
        sitelist.push(this.value);
      });
    } else {
      sitelist.push(site);
    }

    // log to console
    console.log('subdomain: ' + subdomain);
    console.log('site: ' + site);
    console.log('task: ' + task);
    console.log('dbbackup: ' + dbbackup);

    var post_data = [];

    for (var i=0; i < sitelist.length; i++) {
      var item = {
                    'subdomain': subdomain,
                    'site':      sitelist[i],
                    'task':      task,
                    'dbbackup':  dbbackup
                 };

      post_data.push(item);
    }

    window.queueBusy = true

    $.ajax({
      type: "POST",
      url: "/queue/add",
      contentType: 'application/json',
      data: JSON.stringify(post_data),
      dataType: 'json',
      success: updateQueue
    });

    return false;
  });

  $('#queue').on('click', 'tr a.cancel', function() {
    if (confirm('Cancel task?')) {
      window.queueBusy = true

      $.ajax({
        type: "GET",
        url: $(this).attr('href'),
        contentType: 'application/json',
        dataType: 'json',
        success: updateQueue
      });
    }
    return false;
  });

});