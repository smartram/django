// Wrap this function in a closure so we don't pollute the namespace
$(document).ready(function() {

(function getrelated_friends() {
    var scriptval='/friendsumayknow/'  ;
    //$("#left").load(scriptval);
	  $.ajax({
        url: scriptval,
        type: 'GET',
        success: function(data) {
	       var htmlcode=data['html'];
	     	$("#umayknow").append(htmlcode).html();
			resize_images();
    		},
         complete: function() {
            // Schedule the next request when the current one's complete
            }
 	   }); // end ajax
  
    
}) ();


});

