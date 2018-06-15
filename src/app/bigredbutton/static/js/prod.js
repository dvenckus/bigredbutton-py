/*
*   javascript: prod.js
*/
$(document).ready(function() {
  
  // Production ----------------------------------------

  $('#tasks-prod').click(function(){
    if ( $(this).val() == 'relscript' ) {
      $('form#deploy-production .control-group.releases').show();
    } else {
      $('form#deploy-production .control-group.releases').hide();
    }
  });


    
  function clearFormProd() {
    $('#subdomains-prod').val(0);
    $('#sites-prod').val(0);
    $('#tasks-prod').val(0);
    $('#releases-prod').val(0);
    $('form#deploy-prod .control-group.releases').hide();
    $('#chk-backup-database-prod').prop('checked', false);
  };


  $('#clearFormProd').click(function() {
    clearFormProd();
    return false;
  });


  $('#btnPushProd').click(function(e) {
    e.preventDefault();
    if (window.pushBusy == true) { return false; }
    var site = $('#sites-prod').val();
    var task = $('#tasks-prod').val();
    var dbbackup = $('#chk-backup-database-prod').prop('checked') ? 1 : 0;
    var relscript = $('#releases-prod').val();

    if (site == '-' || site == '0' ||
        task == '-' || task == '0') {
      alert('Invalid selection');
      return false;
    }
    if ((task == 'relscript') && (relscript == '0')) {
      alert('Invalid selection');
      return false;
    } 
    // now get the filename of the release script
    relscript = $('#releases-prod').text();

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
    if (task == 'relscript') {
      item.relscript = relscript;
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