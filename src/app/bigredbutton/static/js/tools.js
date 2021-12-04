/*
*   javascript: tools.js
*/


$(document).ready(function() {

  updateTaskHistory();

  // Tools -------------------------------------------

  $("input[type='text'], input[type='password']").on("focus", function () {
    $(this).select();
  });

  // Merge -------------------------------------------

  function clearFormToolsMerge() {
    $('#mergeRepo').val(0);
    $('#mergeBranch').val(0);
    $('#mergeTest').prop('checked', true);
  };


  $('#cancelMerge').click(function() {
    clearFormToolsMerge();
  });


  function updateMerge(data, textStatus, jqXHR) {
    if ((textStatus == 'success') && (data.response == true)) {
      window.appendOutput(data.content);
      clearFormToolsMerge();
    }
    window.toolsBusy = false;
    return false;
  } 


  $('#btnMerge').click(function(e) {
    e.preventDefault();

    var mergeRepo = $('#mergeRepo').val();
    var mergeBranch = $('#mergeBranch').val();
    var mergeTest = ( true == $('#mergeTest').prop('checked') ? 1 : 0);

    if (!mergeRepo || !mergeBranch) {
      alert("Missing input values");
      return false;
    }

    merge = {
      task: 'merge',
      mergeRepo: mergeRepo,
      mergeTo: mergeBranch,
      mergeTest: mergeTest
    };

    $.ajax({
      type: "POST",
      url: "/merge",
      contentType: 'application/json',
      data: JSON.stringify(merge),
      dataType: 'json',
      success: updateMerge
    });

    return false;
  });


  // Version -----------------------------------------

  function clearFormToolsVersion() {
    $('#versionRepo').val(0);
    $('#versionIncrementMinor').prop('checked', true);
    $('#versionTest').prop('checked', true);
  };

  $('#cancelVersionUpdate').click(function() {
    clearFormToolsVersion();
  });

  function updateVersion(data, textStatus, jqXHR) {
    console.log('versionup: ' + data.content);
    if ((textStatus == 'success') && (data.response == true)) {
      window.appendOutput(data.content);
      clearFormToolsVersion();
    }
    window.toolsBusy = false;
    return false;
  } 


  $('#btnVersionUpdate').click(function(e) {
    e.preventDefault();

    var versionRepo = $('#versionRepo').val();
    var versionIncrMajor =  ( true == $('#versionIncrMajor').prop('checked') ? 1 : 0);
    var versionIncrMinor = ( true == $('#versionIncrMinor').prop('checked') ? 1 : 0);
    var versionTest = ( true == $('#versionTest').prop('checked') ? 1 : 0);

    if (!versionRepo) {
      alert("Missing repository value");
      return false;
    }

    versionup = {
      task: 'versionup',
      versionRepo: versionRepo,
      versionIncrMajor: versionIncrMajor,
      versionIncrMinor: versionIncrMinor,
      versionTest: versionTest
    };

    $.ajax({
      type: "POST",
      url: "/versionup",
      contentType: 'application/json',
      data: JSON.stringify(versionup),
      dataType: 'json',
      success: updateVersion
    });

    return false;
  });


  // User ---------------------------------------------


  function clearFormToolsUser() {
    
    if ( $('#usersCurrent').length ) {
      // if only able to edit your own account, the #usersCurrent list will not appear
      $('#User.collapse').collapse('hide');
      $('#userFormTitle').text('Add User');
      $('#userRealName').val('');
      $('#userName').val('');
      $('#userRole').val(0);
      $('#userId').val('');
    } else {
      $('#userRealName').val( $('#userRealName').attr('data-orig-value') );
      $('#userName').val( $('#userName').attr('data-orig-value') );
    }
    $('#userPassword').val('');
    $('#userPassword2').val('');
  };

  $('#cancelUser').click(function() {
    clearFormToolsUser();
  });

  

  $('#userFormTitle').click(function() {
    $('#userRealName').focus();
  });



  function updateUsersList(data, textStatus, jqXHR) {
    // updates the users list display with the current items
    console.log('data: ');
    console.log(data);
    console.log('textStatus: ' + textStatus);
    console.log('jqXHR: ');
    console.log(jqXHR);
    if ((textStatus == 'success') && (data.response == true)) {
      if ( $('#usersCurrent').length ) {
        $("#usersCurrent tbody").html(data.content);
      } else {
        // user updating own account
        var userRealName = $('#userRealName').val();
        $('#userRealName').attr('data-orig-value', userRealName);
        $('#userName').attr('data-orig-value', $('#userName').val());
        $("#output").html(data.content);
        $("ul.navbar-nav .nav-link.hello").text("Hello, " + userRealName + "!");
      }
      clearFormToolsUser();
    }
    window.toolsBusy = false
  };


  function validatePassword(password, password2) {
    var msg = '';
    var bError = false;

    // test for non-alphanumeric characters
    var alphanumeric = /^[a-zA-Z0-9]+$/;
    var result = alphanumeric.test(password); 

    if ( password != password2 ) {
      bError = true;
      msg = "Passwords do not match.";
    } else if (password.length < 8 || password.length > 20) {
      bError = true;
      msg = "Password must be 8 to 20 characters in length";
    } else if (!result) {
      // password contains characters that are not allowed
      bError = true;
      msg = "Password must contain only alphanumeric characters";
    }

    if ( bError ) {
      alert(msg);
      $('#userPassword').focus();
      return false;
    }
    return true;
  };


  // Save User (Add or Edit)
  $('#btnSaveUser').click(function(e) {
    e.preventDefault();

    var realname = $('#userRealName').val();
    var username = $('#userName').val();
    var password = $('#userPassword').val();
    var password2 = $('#userPassword2').val();
    var role_id = 0;

    if ( $('#userRole').prop("readonly") ) {
      // user does not have permissions to change role
      role_id = parseInt($('#userRole').attr('data-roleId'));
    } else {
      role_id = parseInt($('#userRole').val());
    }

    var user_id = $('#userId').val();

    if (!user_id.length) {
      // Add User validation (no password exists)
      if ( !realname.length || !username.length || !password.length || !password2.length || !role_id ) {
        alert('Missing user input');
        return false;
      }
      if (!validatePassword(password, password2)) {
        return false;
      }
    } else {
      // Edit User validation (password input optional, but if a password provided, validate it)
      if ( !realname.length || !username.length ) {
        alert('Missing user name');
        return false;
      }
      if ( !role_id && ($('#userRole').prop("readonly") == false) ) {
        alert('Missing user role');
        return false;
      }
      if ( password.length || password2.length) {
        if (!validatePassword(password, password2)) {
          return false;
        }
      }
    }
    
    if (window.toolsBusy == true) { return false; }
    window.toolsBusy = true;

    var user = {
      'user_id':   user_id, 
      'realname':  realname,
      'username':  username,
      'password':  password,
      'role_id':   role_id
    };

    $.ajax({
      type: "POST",
      url: "/user",
      contentType: 'application/json',
      data: JSON.stringify(user),
      dataType: 'json',
      success: updateUsersList
    });
    return false;
  });


  // edit user - setup user form to edit
  $('#usersCurrent').on('click', 'tr a.user-edit', function(e) {
    e.preventDefault();
    window.toolsBusy = true;

    var $selRow = $(this).parent().parent();
    if (!$selRow.length) {
      alert('Parent <tr> not found');
      return false;
    }
    var $user =  $selRow.find('td.userRealName');
    var userId = $user.attr('data-userId');
    var userRealName = $user.text();
    var userName = $selRow.find('td.userName').text();
    var userRoleId = $selRow.find('td.userRoleName').attr('data-roleId');

    $('#User').collapse('show');
    $('#userFormTitle').text('Edit User');
    $('#userRealName').val(userRealName);
    $('#userName').val(userName);
    $('#userRole').val(userRoleId);
    $('#userId').val(userId);

    $('#userRealName').focus();
    window.toolsBusy = false;
    return false;
  });

  // delete user
  $('#usersCurrent').on('click', 'tr a.user-delete', function(e) {
    e.preventDefault();
    if (confirm('Delete user?')) {
      window.toolsBusy = true;

      var href = $(this).attr('href');

      $.ajax({
        type: "GET",
        url: href,
        contentType: 'application/json',
        dataType: 'json',
        success: updateUsersList
      });
    }
    return false;
  });


  // Roles & Permissions -----------------------------------------

  function clearFormToolsRoles() {
    $('#Role.collapse').collapse('hide');
    $('#roleFormTitle').text('Add Role');
    $('#roleName').val('');
    $('#rolePermissions').val(0);
    $('#roleId').val('');
  };

  $('#cancelRole').click(function() {
    clearFormToolsRoles();
  });

  $('#roleFormTitle').click(function() {
    $('#roleName').focus();
  });


  function updateRolesList(data, textStatus, jqXHR) {
    // updates the users list display with the current items
    console.log('data: ');
    console.log(data);
    console.log('textStatus: ' + textStatus);
    console.log('jqXHR: ');
    console.log(jqXHR);
    if ((textStatus == 'success') && (data.response == true)) {
      $("#rolesCurrent tbody").html(data.content);
      clearFormToolsRoles();
    }
    window.toolsBusy = false
  };

  // Save Role (Add or Edit)

  $('#btnSaveRole').click(function(e) {
    e.preventDefault();

    var roleName = $('#roleName').val();
    var roleId = $('#roleId').val();
    var rolePermissions = $('#rolePermissions').val();

    if ( !roleName.length || !rolePermissions.length ) {
      alert('Missing role input');
      return false;
    }
    
    if (window.toolsBusy == true) { return false; }
    window.toolsBusy = true;

    var role = {
      'role_id':           roleId, 
      'role_name':         roleName,
      'role_permissions':  rolePermissions
    };

    $.ajax({
      type: "POST",
      url: "/role",
      contentType: 'application/json',
      data: JSON.stringify(role),
      dataType: 'json',
      success: updateRolesList
    });
    return false;
  });

  // edit role - setup role form to edit
  $('#rolesCurrent').on('click', 'tr a.role-edit', function(e) {
    e.preventDefault();
    window.toolsBusy = true;

    var $selRow = $(this).parent().parent();
    if (!$selRow.length) {
      alert('Parent <tr> not found');
      return false;
    }
    var $role =  $selRow.find('td.roleName');
    var roleId = $role.attr('data-roleId');
    var roleName = $role.text();
    var rolePermissions = []
    
    $selRow.find('td.rolePermissions ul.permissions li.permission').each(function() {
      rolePermissions.push($(this).attr('data-permission-id'));
    });

    console.log("Edit Role: " + roleName);
    console.log("Permissions: " + rolePermissions.toString());


    $('#Role').collapse('show');
    $('#roleFormTitle').text('Edit Role');
    $('#roleName').val(roleName);
    $('#rolePermissions').val(rolePermissions)
    $('#roleId').val(roleId);

    $('#roleName').focus();
    window.toolsBusy = false;
    return false;
  });
  
  
  // delete role
  $('#rolesCurrent').on('click', 'tr a.role-delete', function(e) {
    e.preventDefault();
    if (confirm('Delete role?')) {
      window.toolsBusy = true;

      var href = $(this).attr('href');

      $.ajax({
        type: "GET",
        url: href,
        contentType: 'application/json',
        dataType: 'json',
        success: updateRolesList
      });
    }
    return false;
  });


  // Task History ------------------------------------------------------

  function updateTaskHistory(data, textStatus, jqXHR) {
    // updates the users list display with the current items
    if ((textStatus == 'success') && (data.response == true)) {
      $("#taskHistory tbody").html(data.content);
    }
    window.toolsBusy = false
    currentDateTime = new Date().toLocaleString();
    $('#lastRefreshed').text("Last Updated: " + currentDateTime);
  };


  $('#taskHistoryRefresh').click(function(e) {
    e.preventDefault();
    window.toolsBusy = true;

    var href = $(this).attr('href');

    $.ajax({
      type: "GET",
      url: href,
      //contentType: 'application/json',
      dataType: 'json',
      success: updateTaskHistory
    });

    return false;
  });



  function viewTaskHistoryItem(data, textStatus, jqXHR) {
    // Displays the task history result for a specific item
    var debug = true;
    if ((textStatus == 'success') && (data.response == true)) {
      // display in popup 
      $('#popupViewer .modal-title').html(data.title);
      $('#popupViewer .modal-body').html(data.content);
      $('#popupViewer').modal('show');
    }
    window.toolsBusy = false;
    return false;
  };
  

  /*
  * view full result for a specific item history
  */
  $('#taskHistory').on('click', 'td a.taskHistoryItemView', function(e) {
    e.preventDefault();
    window.toolsBusy = true;

    var href = $(this).attr('href');

    $.ajax({
      type: "GET",
      url: href,
      //contentType: 'application/json',
      dataType: 'json',
      success: viewTaskHistoryItem
    });

    return false;
  });

});
