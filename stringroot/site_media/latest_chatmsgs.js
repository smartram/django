// Wrap this function in a closure so we don't pollute the namespace
$(document).ready(function() {
 var latestchat=function get_latestchat() {

 var name=$("#username").attr("value");
 var urlaction='/getlatestchat?username='+name ;
 
 
        $.ajax({
            url: urlaction,
            type: 'GET',
            dataType: 'json',
            async: false,
            success: function(data) {
		        if(data["status"]==0)
     			{
				var htmlcode=data["html"];
				
				$("#list_chat").append(htmlcode).html();
				var objDiv = document.getElementById("chat");
				objDiv.scrollTop = objDiv.scrollHeight;

     			}

            }, // end success
            complete: function() {
	      		// Schedule the next request when the current one's complete
    		  	setTimeout(get_latestchat, 60000);
    		} // end complete. 

        });// end ajax

};

setTimeout(latestchat,30000);
 

});
