$(document).ready(function() {
  // Retrieve the CSRF token from the meta tag
  var csrf_token = $('meta[name="csrf-token"]').attr('content');

  // Set up AJAX requests to include the CSRF token
  $.ajaxSetup({
    headers: {
      'X-CSRFToken': csrf_token
    }
  });

  // Handle Create Folder Form Submission
  $('#createFolderForm').on('submit', function(e) {
    e.preventDefault(); // Prevent default form submission
    var formData = $(this).serialize();
    $.ajax({
      url: window.createFolderUrl, // Use the URL defined in the HTML
      type: 'POST',
      data: formData,
      success: function(response) {
        // Close the modal
        $('#createFolderModal').modal('hide');
        // Update the folders list
        $('#foldersList').append('<li class="list-group-item">' + response.folder_name + '</li>');
        // Clear the form
        $('#createFolderForm')[0].reset();
        // Show a success message
        $('#folderMessages').html('<div class="alert alert-success">Folder created successfully!</div>');
      },
      error: function(xhr) {
        // Handle errors
        $('#folderMessages').html('<div class="alert alert-danger">' + xhr.responseText + '</div>');
      }
    });
  });

  // Handle Create Task Form Submission
  $('#createTaskForm').on('submit', function(e) {
    e.preventDefault();
    var formData = $(this).serialize();
    $.ajax({
      url: window.createTaskUrl, // Use the URL defined in the HTML
      type: 'POST',
      data: formData,
      success: function(response) {
        $('#createTaskModal').modal('hide');
        $('#tasksList').append('<li class="list-group-item">' + response.task_name + ' - Due ' + response.deadline + '</li>');
        // Clear the form
        $('#createTaskForm')[0].reset();
        // Show a success message
        $('#taskMessages').html('<div class="alert alert-success">Task created successfully!</div>');
      },
      error: function(xhr) {
        $('#taskMessages').html('<div class="alert alert-danger">' + xhr.responseText + '</div>');
      }
    });
  });
});
