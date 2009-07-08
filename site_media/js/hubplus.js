var widget_map = {'Profile':{'about':'text_wysiwyg'}
		 };

var editing = function () {
    //jq('#section_tab_navigation').tabs();
    tab_history('profile');
    jq('.editable').each(function (i, ele) {
	var element_id = jq(ele).attr('id');
	var prop_data = element_id.split('-');
	var object_type = prop_data[0];
	var object_id = prop_data[1];
	var object_prop = prop_data[2];
	try {
	    var widget_type = widget_map[object_type][object_prop];
	} catch(e) {
            var widget_type = 'text_small';
	}
	if (widget_type == 'image') {
            new Upload(object_id, object_type, object_prop, ele, ele, relative_url +'edit/');
            return;
        }
	var edit_event = 'click';
	var clickToEdit = "Click To Edit";
	var page_name = jq('#page_path_name').attr('class');
	inplace_editor(element_id, 'field/' + object_type + '/' + object_prop + '/', {callback: function (form, val) {
	    return [{name: 'value', value: val}];
	    },
            object_type: object_type,
            object_id: object_id,
            ui_type: widget_type,
            edit_event: edit_event,
            clickToEditText: clickToEdit,
            widget_id: element_id + '_widget',
            widget_name: element_id,
            property: object_prop,
            value: jq('#' + element_id).html(),
            loadTextURL:  'field/' + object_type + '/' + object_prop + '/?default=' + encodeURIComponent(jq(ele).html())
	});
    });
};
var tag_list = function (ele) {
    var manager = jq(ele);
    var tag_type = manager.find('.tag_type').val();
    var append_tag = function (data) {
	if (data.added === false) {
	    manager.find('.error_message').html("You have already tagged " + data.tagged + " as having the " + data.tag_type + " <em>" +  data.keyword + "</em>");
	    return;
	}
	var tag = jq('<span><a href="tag/' + data.keyword + '" class="tag option">' + data.keyword + '</a><a class="delete_tag" href="./delete_tag/">X</a></span>');
	manager.find('.tag_list').append(tag);
	manager.find('input.tag_value').val("");
	manager.find('.error_message').html("");
    };
    var delete_tag = function (tag, data) {
	if (data.deleted === true) {
	    tag.remove();
	}
    };

    manager.find('.tag_value').autocomplete('autocomplete_tag/'+ manager.find('.tag_type').val()+ '/', {width: 175,
													matchSubset: false,
													selectFirst: false,
													max:10});

    manager.find('.add_tag').click(function () {
	jq.post('add_tag/', jq(this).parent().serializeArray(), append_tag, "json");
	return false;
    });
    var delete_tags = '#'+ manager.attr('id') + ' .delete_tag';
    jq(delete_tags).live('click', function () {
	var tag_value = jq(this).prev().html();
	var tag_data = [{name : 'tag_type', value : tag_type},
			{name : 'tag_value', value : tag_value}];
	var tag = jq(this).parent();
	jq.post('delete_tag/', tag_data, function(data) {
	    delete_tag(tag, data);
	}, "json");
	return false;
    });
};
var setup_tag_lists = function () {
    jq('.tag_manager').each(function(i, ele) {
	tag_list(ele);
    });
};
var profile = function () {
    editing();
    setup_tag_lists();
    //jq.getJSON('map_tags/', {}, init_rgraph);
};
jq(document).ready(function () {
    profile();
});
