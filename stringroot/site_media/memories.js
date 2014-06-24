$(document).ready(function() {

$("#loading").hide();

$('input[type="submit"]').attr('disabled','disabled');

$("#hexabutton").css("color","white");



var bind_delete=function(){
$("ul a.delpost").click(function() {

var jthis=$(this);
var value="/deletepost/" + $(jthis).attr("id") + "?mem=true";

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

/*

$('#memform').ajaxForm({

beforeSubmit: function() { 
$("#loading").show();

},

success: function(data) {
$("#loading").hide();
$("#hexatext").val('');
$("#hexafile").val('');
$("#response").val('');
var htmlcode=data["html"];
if(data["status"]==0)
{

$("#recent_added").prepend(htmlcode).html();
bind_delete();

}
else
{
$("#response").empty();
$("#response").addClass('alertmsg');
$("#response").append(htmlcode).html();
$("#response").slideDown("slow");
setTimeout(function() { $("#response").slideUp(200) }, 6000);
}

} 

});
*/

// for each "Characters remaining: ###" element found
$('.remaining').each(function(){
// find and store the count readout and the related textarea/input field

var $count = $('.count',this);
var $input = $(this).prev();
// .text() returns a string, multiply by 1 to make it a number (for math)
var maximumCount = $count.text()*1;
// update function is called on keyup, paste and input events
var update = function(){

if($input.val().length > 0)
{
$('input[type="submit"]').removeAttr('disabled');

$("#hexabutton").css("color","#fff");

}
var before = $count.text() * 1;
var now = maximumCount - $input.val().length;
// check to make sure users haven't exceeded their limit
if ( now < 0 ){
$('input[type="submit"]').attr('disabled','disabled');

$("#hexabutton").css("color","brown");

var str = $input.val();
$input.val( str.substr(0,maximumCount) );

}
if(now == maximumCount)
{

$('input[type="submit"]').attr('disabled','disabled');

$("#hexabutton").css("color","brown");

}

// only alter the DOM if necessary
if ( before != now ){

$count.text( now );

}

};
// listen for change (see discussion below)
$input.bind('input keyup paste', function(){setTimeout(update,0)} );
// call update initially, in case input is pre-filled
update();
}); // close .each()

$('.memlinks').click(function() {
  href=$(this).attr("href");
$.ajax({
            url: href,
            type: 'get',
            dataType: 'json',
            async: false,
            success: function(data) {
                result = data['html'];
                status=data['status'];
                if(status == 0){
                $("#list_posts").empty();
                $("#list_posts").append(result);
                }
                else{
                $("#list_posts").prepend(result);
                }
            } // end success
        });
     
  return false;
  

});
}); // end document ready


