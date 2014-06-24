$(document).ready(function() {

$("#addfriend").click(function() {
var value = $(this).attr("href");

$("#middle").empty();

$("#middle").load(value);

return false;
});

});

