$(document).ready(function() {

$("#invitations").ajaxForm({

beforeSubmit: function() { 
},

success: function(data) {
 $("#response").empty();
 $("#response").addClass('alertmsg');
$("#response").html(data);
$("#response").slideDown("slow");
setTimeout(function() { $("#response").slideUp(200) }, 6000);

  } // end success

}); // end ajax

}); // end doc
