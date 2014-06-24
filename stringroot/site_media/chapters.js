$(document).ready(function(){
$('ul.sub-menu').hide();
$('ul li a).click(function() {
    $(this).parent().children('ul.sub-menu').toggle();
    
});​
});
