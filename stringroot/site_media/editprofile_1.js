$(document).ready(function() {

$("#editform").ajaxForm({

beforeSubmit: function() { 
},

success: function(data) {
 $("#response").empty();
// $("#response").append(data).html();
/*
$("#response").addClass('alertmsg');
 $("#response").append(data).html();
$("#response").slideDown("slow");
setTimeout(function() { $("#response").slideUp(200) }, 10000);
*/
document.location.href = '/editprofile/';
  }

});


$("#passform").ajaxForm({

beforeSubmit: function(){
},

success: function(data){
  $("#response1").empty();
  $("#response1").append(data['html']).html();
}

});

});

