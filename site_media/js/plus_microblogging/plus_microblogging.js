function status(ele) {
    var manager = jq(ele);
    manager.change( function() { 
	    var ele_time = manager.find('.label_time');
	    ele_time.html('Just now'); // XXX i18n in js?
	} );
}

function status_form(ele) {
    var manager = jq(ele);

    var edit = jq(manager.find('.edit'));
    var show = jq(manager.find('.show'));
    var toggle = jq(manager.find('.toggle'));


    if (edit.find('.starts_hidden').val() == "True") {
        edit.hide();
    } else {
	show.hide();
    }

    function toggle_all() {
	show.toggle();
	edit.toggle();
    }

    toggle.click(function(e) {
	    toggle_all();
	} );

    show.click(function(e) {
	    toggle_all();
	});
    

}

var plus_status_ready = function () {
    jq('#head_title_status').each(function(i, ele) {
            status(ele);
    });

    jq('.status_form').each(function(i,ele) {
	    status_form(ele);
    });
};

