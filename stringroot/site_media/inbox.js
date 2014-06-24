$(document).ready(function() {

$("button.delall").click(function() {

var value=$(this).attr("id"); 
//alert("clicked");
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
        }); // end ajax
    }
});
 $(this).parent().remove();
 var url="/delall/"+ value;
$.deleteValues(url);
var count=$("#list_messages li").size();
if (count == 0)
{
$("#list_messages").append('<p style="color:blue; text-align:center"> <b> Inbox empty Click <a href="/">Here </a> . </b> </p>').html();
}
return false;

});


});

