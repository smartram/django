$(document).ready(function() {


$('input[type="submit"]').attr('disabled','disabled');

$("#commentbutton").css("color","brown");


$('#commentform').ajaxForm({

beforeSubmit: function() {  },

success: function(data) {

$("#commenttext").val('');

var htmlcode=data["html"];
if(data["status"]==0)
{
$("#list_comments").prepend(htmlcode).html();

bind_reportspam();
}
//reset the submit button.
var $count = $('.remaining span').text('80') ;
$('input[type="submit"]').attr('disabled','disabled');
$("#commentbutton").css("color","brown");
 
}

});


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

$("#commentbutton").css("color","#fff");

}
var before = $count.text() * 1;
var now = maximumCount - $input.val().length;
// check to make sure users haven't exceeded their limit
if ( now < 0 ){
$('input[type="submit"]').attr('disabled','disabled');

$("#commentbutton").css("color","brown");

var str = $input.val();
$input.val( str.substr(0,maximumCount) );

}
if(now == maximumCount)
{

$('input[type="submit"]').attr('disabled','disabled');

$("#commentbutton").css("color","brown");

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


var bind_reportspam=function(){
$("a.delcomment").click(function() {

var jthis=$(this);
var value="/reportspam/" ;
var idval= $(this).attr("id");

jQuery.extend({

    deleteComments: function(url,jthis) {
		var result=null;

        $.ajax({
            url: url,
            type: 'POST',
            data: {'id':idval},
            dataType: 'json',
            success: function(data) {
                result = data['html'];
            }
        }); // end ajax       
    }
});

jConfirm('Are you sure you want to delete this Comment?', 'Confirmation Dialog', function(r) {
										
  if(r==true)
  {
	(jthis).parent().remove();
	var htmlStore = $.deleteComments(value,jthis);
    }
 }); // end jConfirm 
   
  return false; // prevent default
 
}); // end click
} // end function bind_reportspam

bind_reportspam();
}); // end document ready


