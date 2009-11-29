function status(ele) {
    var manager = jq(ele);
    manager.change( function() { 
	    var ele_time = manager.find('.label_time');
	    ele_time.html('Just now'); // XXX i18n in js?
	    // XXX We should
	} );
}


var plus_status_ready = function () {
    jq('#head_title_status').each(function(i, ele) {
            status(ele);
        });
};

