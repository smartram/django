$(document).ready(function() {

 var objDiv = document.getElementById("chatwindow");
 objDiv.scrollTop = objDiv.scrollHeight;

$('#chatform').ajaxForm({

	beforeSubmit: function() { },

	success: function(data) {
	 $("#empty").val('');
	 $("#chattext").val('');
	 var htmlcode=data["html"];
	 $("#list_chat").append(htmlcode).html();
	 //reset the submit button.
	var $count = $('.remaining span').text('80') ;
	$('input[type="submit"]').attr('disabled','disabled');
	$("#hexabutton").css("color","brown");
	 // set the height now.
	 var objDiv = document.getElementById("chatwindow");
	 objDiv.scrollTop = objDiv.scrollHeight;

	}

}); 


$('.remaining').each(function(){
// find and store the count readout and the related textarea/input field

var $count = $('.count',this);
var $input = $("#chattext");
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



}); // end doc
