/*
*   javascript: preprod.js
*/
$(document).ready(function() {
  
  // Pre-Production ----------------------------------------

  function clearFormPreProd () {
    $('#subdomains-preprod').val(0);
    $('#sites-preprod').val(0);
    $('#tasks-preprod').val(0);
    $('#releases-preprod').val(0);
    $('form#deploy-preprod .control-group.releases').hide();
    $('#chk-backup-database-preprod').prop('checked', false);
  };

  $('#clearFormPreProd').click(function () {
    clearFormPreProd();
  });

  
  clearFormPreProd();

  window.getQueue = function() {
    if (window.queueBusy == true) { return; }
    window.queueBusy = true;

    var href = $('#queue').attr('data-href');

    $.ajax({
      type: "GET",
      cache: false,
      url: href,
      dataType: 'json',
      success: function(data, textStatus, jqXHR) {
        // updates the queue display with the current items
        var debug = true;
        if ((textStatus == 'success') && (data.response == true)) {
          //console.log('updatePreProdPage: ' + data.content)
          if (data.content.length) {
            $('#queue-body').html(data.content);
          }
          clearFormPreProd();
        }
        window.queueBusy = false;
      }
    });
  };


  $('#btnQueuePreprod').click(function() {
    var subdomain = $('#subdomains-preprod').val();
    var site = $('#sites-preprod').val();
    var task = $('#tasks-preprod').val();

    if (window.queueBusy) return false;

    if (subdomain == '-' || subdomain == '0' ||
        site == '-' || site == '0' ||
        task == '-' || task == '0') {
      alert('Invalid selection');
      return false;
    }

    window.queueBusy = true;

    var dbbackup = $('#chk-backup-database-preprod').prop('checked') ? 1 : 0;
    var sitelist = [];

    if (site == 'all') {
      $('#sites-preprod option.site').each(function() {
        sitelist.push(this.value);
      });
    } else if (site == 'health') {
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

    var tasklist = [];
    var postdata={};

    for (var i=0; i < sitelist.length; i++) {
      var item = {
                    'subdomain': subdomain,
                    'site':      sitelist[i],
                    'task':      task
                 };

      if ((task == 'push') || (task == 'sync')) {
        item.dbbackup = dbbackup;
      } 

      tasklist.push(item);
    }
    postdata['tasks'] = tasklist;

    var href = $(this).attr('data-href');

    $.ajax({
      type: "POST",
      cache: false,
      url: href,
      contentType: 'application/json',
      data: JSON.stringify(postdata),
      dataType: 'json',
      success: function(data, textStatus, jqXHR) {
        //if ((textStatus == 'success') && (data.response == true)) {
        //  clearFormPreProd();
        //}
        //window.queueBusy = false;
      }
    });
    clearFormPreProd();
    window.queueBusy = false;
    return false;
  });


  $('#queue').on('click', 'tr a.cancel', function() {
    if (confirm('Cancel task?')) {
      window.queueBusy = true;

      $.ajax({
        type: "GET",
        cache: false,
        url: $(this).attr('href'),
        // contentType: 'application/json',
        dataType: 'json',
        success: function(data, textStatus, jqXHR) {
          // if ((textStatus == 'success') && (data.response == true)) {
          //   clearFormPreProd();
          // }
          // window.queueBusy = false;
        }
      });
    }
    clearFormPreProd();
    window.queueBusy = false;
    return false;
  });

});