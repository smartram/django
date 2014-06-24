$(document).ready(function() {

$("ul .posts").hover(
  function () {
    $(this).find(".sharedpost").show();
    $(this).find(".delpost").show();
  }, 
  function () {
    $(this).find(".sharedpost").hide();
   $(this).find(".delpost").hide();
  }
);

var bind_delete=function(){

$("ul a.delpost").click(function() {

var jthis=$(this);
var value="/deletepost/" + $(jthis).attr("id");

jQuery.extend({
    deleteValues: function(url) {
        var result = null;
        $.ajax({
            url: url,
            type: 'get',
            dataType: 'json',
            async: false,
            success: function(data) {
                result = data['html'];
            }
        });
       return result;
    }
});
	jConfirm('Are you sure you want to delete this post?', 'Confirmation Dialog', function(r) {
										
					if(r==true)
					{
					    $(jthis).parent().remove();
						var htmlStore = $.deleteValues(value);

					}
						
						
						
	}); // end jConfirm
	
  
   
    return false; // prevent default

}); // end click
};

bind_delete();

$("ul a.delpost").hide();
 
 }); // end doc
