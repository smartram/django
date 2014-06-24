$(document).ready(function() {
delfriend=function(){
$(".deletefriend").click(function() {

var action=$(this).attr("value");
$(this).parent().remove();
$(this).remove();
$.ajax({
type: 'GET',
url: action,
dataType: 'html',
success: function(html, textStatus) {
},
error: function(xhr, textStatus, errorThrown) {
alert('An error occurred! ' + errorThrown);
}

}); // end ajax 
return false;
});
};

var bind_unfriend=function(){
$("button.Unfriend").click(function(){
var action="/friend_delete/" ;
var value=$(this).attr("user");
var actionurl=action + value ;
$(this).text("Add Friend");
$(this).removeClass("Unfriend");
$(this).addClass("Addfriend");
bind_addfriend();
$.get(actionurl);
return false;
});
};


var bind_addfriend=function(){
$("button.Addfriend").click(function(){

var action="/friend_add/" ;
var value=$(this).attr("user");
var actionurl=action + value ;
$(this).text("Unfriend");
$(this).removeClass("Addfriend");
$(this).addClass("Unfriend");
bind_unfriend();
$.get(actionurl);
return false;
});
};

bind_addfriend();
bind_unfriend();
delfriend();


});





