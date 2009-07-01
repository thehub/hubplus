(function($){
    $.fn.confirm_action = function(options) {
        options = $.extend({action:function(){$('body').load(this.attr('href'))},
                            message:'Are you sure you want to delete this resource group? ',
                            cancel: function(dialog, action_link, options){$.cancel_action(dialog, action_link, options)}
                           }, options);
        return this.each(function() {
             $.set_dialog_listen(this, options);
	});
    };
    $.set_dialog_listen = function(action_link, options) {
        $(action_link).one('click', function() {
            $.confirm(action_link, options);
            return false;
        });
    };
    $.cancel_action = function(dialog, action_link, options) {
         dialog.remove();
         $.set_dialog_listen(action_link, options);
         return false;
    };
    $.confirm = function(action_link, options) {
        action_link = $(action_link);
        action_link.unbind("click");
        action_link.click(function(){return false;});
        $("<div class='confirm_dialog'>"+options.message+"<br /><a class='confirm_action' style='cursor:pointer;'>Confirm</a>  <a class='cancel_action' style='cursor:pointer;'>Cancel</a></div>").insertAfter(action_link);
        var dialog = action_link.next();
        dialog.find('.cancel_action').click(function(){options.cancel(dialog, action_link, options)});
        dialog.find('.confirm_action').click(function(){options.action(action_link)});
    };
})(jQuery);
