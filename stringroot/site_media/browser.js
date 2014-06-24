(function () {

  if(!$.support.opacity) // This is IE, support overflow
   {
     $('body').css('overflow','auto');
	$('html').css('overflow','auto');

   }

}());

