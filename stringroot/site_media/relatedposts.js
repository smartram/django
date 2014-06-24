// Wrap this function in a closure so we don't pollute the namespace
$(document).ready(function() {

(function getrelated_attachments() {
    var code=$("#postcode").attr("value");
    var scriptval='/getrelatedposts/' + code ;
    //$("#left").load(scriptval);
	  $.ajax({
        url: scriptval,
        type: 'GET',
        success: function(data) {
	       var htmlcode=data['html'];
	     	$("#related_posts").append(htmlcode).html();

    		},
         complete: function() {
            // Schedule the next request when the current one's complete
            }
 	   }); // end ajax
  
    
}) ();


});

