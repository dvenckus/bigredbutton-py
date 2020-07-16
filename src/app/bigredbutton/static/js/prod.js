/*
*   javascript: prod.js
*/
$(document).ready(function() {
  
  // Production ----------------------------------------

    
  function clearFormProd() {
    $('#subdomains-prod').val(0);
    $('#sites-prod').val(0);
    $('#tasks-prod').val(0);
    $('#releases-prod').val(0);
    $('form#deploy-prod .control-group.releases').hide();
    $('#chk-backup-database-prod').prop('checked', true);
    window.pushBusy = false;
  };


  $('#clearFormProd').click(function() {
    clearFormProd();
    return false;
  });

  clearFormProd();


  $('#btnPushProd').click(function(e) {
    e.preventDefault();
    if (window.pushBusy == true) { return false; }
    var site = $('#sites-prod').val();
    var task = $('#tasks-prod').val();
    var dbbackup = $('#chk-backup-database-prod').prop('checked') ? 1 : 0;

    if (site == '-' || site == '0' ||
        task == '-' || task == '0') {
      alert('Invalid selection');
      return false;
    }


    window.pushBusy = true;

    // log to console
    console.log('site: ' + site);
    console.log('task: ' + task);
    console.log('dbbackup: ' + dbbackup);

    var item = {
                  'site':      site,
                  'task':      task
              };
    if ((task == 'push') || (task == 'sync')) {
      item.dbbackup = dbbackup;
    }

    $.ajax({
      type: "POST",
      url: "/push",
      contentType: 'application/json',
      data: JSON.stringify(item),
      dataType: 'json',
      success: function(data, textStatus, jqXHR) {
        if (textStatus == 'success' && data.response == true) {
          console.log('push: ' + data.content);
          window.appendOutput(data.content);
          clearFormProd();
        }
        window.pushBusy = false;
      }
    });
    return false;
  });
});