// Wrap this function in a closure so we don't pollute the namespace
$(document).ready(function() {

var getallcount=function getallfcount() {
var username=$("#userpageval").attr('value');
var scriptval='/getcount/' + username;

  $.ajax({
    url: scriptval,
    type: 'GET',
    success: function(data) {
    var friendscount=data['friendscount'];
    var fanscount=data['fanscount'];
     
     
     $("#friendscount").text("Friends " + friendscount);
     $("#viewfans").text("Fans " + fanscount);

    },
    complete: function() {
      // Schedule the next request when the current one's complete
    }
  }); // end ajax
  
};

getallcount();
});