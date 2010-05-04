function links(ele) {
    var manager = jq(ele);
    var target_id = manager.find('.target_id').val();
    var target_class = manager.find('.target_class').val();
    manager.find(".submit_link").live('click', function(e) {
	var args = manager.find(':input').serializeArray();
	jq.post(manager.find('.link_form').attr('target'), args, complete, "json");
	return false;
    });
    var complete = function(json) {
	if (json.new_link) {
	    append_link(json.new_link);
	} else if (json.list_and_form) {
	    manager.html(json.list_and_form);
	}
    };
    var append_link = function(new_link) {
	manager.find(".list_of_links").children('li:last').prev().append(new_link);
	manager.find("input.link_text").val("").focus();
	manager.find("input.url").val("");
	manager.find(".error_message").html("");
    };
    manager.find(".remove_link").live('click', function() {
	var link = jq(this);
	jq.get(link.attr('id'), [], function(data) {
	    if (data.deleted) {
		link.parent().parent().remove();
	    } else {
		link.parent().append("<span class='error_message'>Cannot delete link<span>");
	    }
	}, "json");
	return false;
    });
    return true;
}


var plus_links_ready = function () {
    jq('.external_links').each(function(i, ele) {
	links(ele);
    });

};
