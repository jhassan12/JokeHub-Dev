$(document).ready(function(){
	var obj = $('.alert-message')

	obj.removeClass('alert-message')
   	obj.addClass('alert-info')

   	$(".content-container .delete, .icon-container .heart").click(function(){
		window.location.href = $(this).data("url")
	})
})