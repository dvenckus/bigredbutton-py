/*
*   javascript: brb.js
*
*   this is the home for the generic and overall use stuff
*/
// $(document).one('ready', function(){
//   $('#tab-preprod').tab('show');
//   $('#queue-panel').show();
//   $('#output-panel').hide();
// });

$(document).ready(function() {

  // Tab actions ------------------------------------------
  $('#tabs a').click(function() {
    $(this).tab('show');
  });

  $('#tab-preprod').click(function(e) {
    $('#queue-panel').show();
    $('#output-panel .panel-heading')
      .removeClass('tools-output-heading')
      .removeClass('prod-output-heading')
      .addClass('preprod-output-heading');
    //$('#output-panel').hide();
    return false;
  });
  $('#tab-tools').click(function(e) {
    $('#queue-panel').hide();
    $('#output-panel .panel-heading')
      .removeClass('preprod-output-heading')
      .removeClass('prod-output-heading')
      .addClass('tools-output-heading');
    //$('#output-panel').show();
    return false;
  });
  $('#tab-production').click(function(e) {
    $('#queue-panel').hide();
    $('#output-panel .panel-heading')
      .removeClass('tools-output-heading')
      .removeClass('preprod-output-heading')
      .addClass('prod-output-heading');
    //$('#output-panel').show();
    return false;
  });

  $('div.control-group.releases').hide();

});
