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
    var ta = jq(edit.find('#new_tweet'));
    
    jq(ta).val('');

    if (edit.find('.starts_hidden').val() == "True") {
        edit.hide();
    } else {
	show.hide();
        toggle.hide();
    }

    function toggle_all() {
	show.toggle();
	edit.toggle();
    }

    toggle.click(function(e) {
	    toggle_all();
	    toggle.hide();
	} );

    show.click(function(e) {
	    toggle_all();
	});
    
    ta.keypress(function(e) {
	    var s = jq(this).val();
	    var free = 140 - s.length;
	    manager.find('.no_chars').html(free + " left");
	    if (free < 1) {
		s = s.substr(0,139);
		jq(this).val(s);
	    }
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

