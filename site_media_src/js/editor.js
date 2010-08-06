var wiki_edit = function () {
    var hist_data = jq('#history_data');
    hist_data.hide();
    var checkboxes = function () {
	var first_checked = jq('#history input.first:checked');
	var second_checked = jq('#history input.second:checked');
	var first_high = all_second.index(second_checked.get(0));
	var second_low = all_first.index(first_checked.get(0));
	all_first.each(function (i, ele) {
	    if (i < first_high) {
		jq(ele).removeAttr('disabled').css('visibility', 'visible');
	    } else {
		jq(ele).css('visibility', 'hidden').attr('disabled', 'disabled');
	    }
	});
	all_second.each(function (i, ele) {
	    if (i > second_low) {
		jq(ele).removeAttr('disabled').css('visibility', 'visible');
	    } else {
		jq(ele).css('visibility', 'hidden').attr('disabled', 'disabled');
	    }
	});
    };
    var display_version = function(json) {
	jq.each(json, function (key, val) {
 	    hist_data.find('#ver_' + key).html(val);
	    hist_data.show();
	});
	window.location.hash = "#history_data"; //does this need to refer to an href of an anchor tag to work cross browser?
    };
    jq('.compare').click(function () {
	var ver_1_id = jq('#history input.first:checked').closest('tr').attr('id').split('-')[1];
	var ver_2_id = jq('#history input.second:checked').closest('tr').attr('id').split('-')[1];
	var action = jq('#history form').attr('action');
	jq.getJSON(action, {'ver_1':ver_1_id, 'ver_2':ver_2_id}, display_version);
	return false;
    });
    var all_first = jq('#history input.first');
    var all_second = jq('#history input.second');
    all_second.click(checkboxes);
    all_first.click(checkboxes);
    checkboxes();
    jq('div#history tr.version_entry').click(function (event) {
	var target = event.target;
	if (jq(target).hasClass('view_old')) {
	    jq.getJSON(jq(target).attr('href'), {'ver_id':jq(this).attr('id').split('-')[1]}, display_version);
	    return false;
	}
	return true;
    });
    if (jq('.wiki_edit').length) {
	var myEditor;
	jq('#xcontent').each(function (i, ele){
	    var target = jq(ele).find('textarea');
	    var config = {
		height: target.height(),
		width: target.width(),
		dompath: true, //Turns on the bar at the bottom
		animate: true, //Animates the opening, closing and moving of Editor windows
		autoHeight: true
	    };
	    myEditor = new YAHOO.widget.Editor(target.get(0), config);
	    myEditor._defaultToolbar.titlebar = false;
	    myEditor.render();
	    jq('#page_edit_form').find('#edit_submit').one('click', function () {
		myEditor.saveHTML();
		jq('#page_edit_form').submit();
		return false;
	    });
	    jq('#page_edit_form').find('#preview').one('click', function () {
		myEditor.saveHTML();
		jq(this).click();
		return false;
	    });
	});
    }
};
