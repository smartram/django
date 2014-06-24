// Wrap this function in a closure so we don't pollute the namespace
$(document).ready(function() {
var latestwall=function worker() {
var scriptval='/getlatestwallposts' ;


  $.ajax({
    url: scriptval,
    type: 'GET',
    success: function(data) {
    var htmlcode=data["html"];
    
     if(data["status"]==0)
     {
     $("#list_posts").prepend(htmlcode).html();
     }

    },
    complete: function() {
      // Schedule the next request when the current one's complete
     	 setTimeout(worker, 60000);
    },
    timeout: 2000
  }); // end ajax
  
} // end function

setTimeout(latestwall,60000);

});