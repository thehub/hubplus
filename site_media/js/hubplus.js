var widget_map = {
    'Profile':{'about':'text_wysiwyg',
               'find_out':'text_wysiwyg',
	       'project_stage':'text_wysiwyg',
	       'place': 'gmap'
    },
    'TgGroup':{'description':'text_wysiwyg'},
    'Resource':{'description':'text_wysiwyg'}
};

var editing = function () {
    tab_history('section_tab_navigation');
    jq('.more').click(function () {
	var trunc = jq(this).parent();
	trunc.hide();
	trunc.next().show();
	return false;
    });
    jq('.less').click(function () {
	var trunc = jq(this).parent();
	trunc.hide();
	trunc.prev().show();
	return false;
    });
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
	inplace_editor(element_id, "/lib/attribute/" + object_id + '/' + object_type + '/' + object_prop + '/', {callback: function (form, val) {
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
            loadTextURL: '/lib/attribute/' + object_id + '/' + object_type + '/' + object_prop + '/?default=' + encodeURIComponent(jq(ele).html())
	});
    });
};


var tag_list = function (ele) {
    var manager = jq(ele);
    var delete_url = manager.find('ul .first a.delete_tag').attr('href');
    var tag_type = manager.find('.tag_type').val();
    var tagged_id = manager.find('.tagged_id').val();
    var tagged_class = manager.find('.tagged_class').val();

    var append_tag = function (data) {
	if (data.added === false && !data.error_message) {
	    manager.find('.error_message').html("You have already tagged " + data.tagged + " as having the " + data.tag_type + " <em>" +  data.keyword + "</em>");
	    return;
	} else if (data.error_message) {
	    manager.find('.error_message').html(data.error_message);
	    return;
	}
	var tag = jq('<li><a href="' + data.tag_url + '" class="tag option">' + data.keyword + '</a><a class="delete_tag" href="'+ delete_url +'">X</a></li>');
	manager.find('.tag_list').append(tag);
	manager.find('input.tag_value').val("");
	manager.find('.error_message').html("");
    };
    var delete_tag = function (tag, data) {
	if (data.deleted === true) {
	    tag.remove();
	}
    };
    manager.find('.tag_value').autocomplete(manager.find('.tag_value').attr('id') + '?tagged_class=' + manager.find('.tagged_class').val()+
					    '&tagged_id=' + manager.find('.tagged_id').val(),
                                            {width: 175,
					     matchSubset: false,
					     selectFirst: false,
					     max:10}
					   );

    manager.find('.add_tag').click(function () {
	var args = jq(this).parent().find(':input').serializeArray();
	jq.post(manager.find('.add_tag_form').attr('id'), args, append_tag, "json");
	return false;
    });
    var delete_tags = '#'+ manager.attr('id') + ' .delete_tag';
    jq(delete_tags).live('click', function () {
	var tag_value = jq(this).prev().html();
	var tag_data = [{name : 'tag_type', value : tag_type},
			{name : 'tag_value', value : tag_value},
			{name : 'tagged_class', value : tagged_class},
			{name : 'tagged_id', value : tagged_id}
			];
	var tag = jq(this).parent();
	jq.post(delete_url, tag_data, function(data) {
	    delete_tag(tag, data);
	}, "json");
	return false;
    });
};
var setup_tag_lists = function () {
    jq('.tag_manager').each(function(i, ele) {
	tag_list(ele);
    });
    jq('.goto_tag').autocomplete(jq('.goto_tag').attr('id'), {width: 175,
							      matchSubset: false,
							      selectFirst: false,
							      max:10});
};

var setup_maps = function () {
    jq("[id$='-place']").each(function () {
	create_map(jq(this), plot_point);
    });
};
var get_add_content = function (ele) {
    var overlay_content = jq('#overlay_content');
    jq('div.close').click(function () {
        overlay_content.html("");
    });
    var set_auto_complete = function (auto_area) {
	auto_area.find('#autocomplete_group').autocomplete('/groups/autocomplete/', {
	    formatItem:function(item, i, max) {
		return item.display_name;
	    },
	    width: 175,
	    matchSubset: false,
	    selectFirst: true,
	    max:6,
	    dataType: 'json',
	    parse: function(data) {
		var rows = new Array();
		for(var i=0; i<data.length; i++){
		    rows[i] = { data:data[i], value:data[i].id, result:data[i].display_name};
		}
		return rows;
	    }
	}).result(function(event, data, formatted) {
	    overlay_content.find('#group_display_name').html(data.display_name);
	    overlay_content.find('#group_input').val(data.id);
	    overlay_content.find('#choose_type li').each(function (i, ele) {
		if (data.interfaces.indexOf(ele.id) == -1) {
		    jq(ele).attr('disabled', 'disabled').addClass('cannot_add');
		} else {
		    jq(ele).removeAttr('disabled').removeClass('cannot_add');
		}
	    });
	    overlay_content.find('.hidden').show();
	    overlay_content.find('#create_content').removeAttr('disabled');
	    auto_area.hide();
	    auto_area.find('#autocomplete_group').val("");
	});
    };
    jq.get(ele.attr('href'), function(data, status) {
	var initialize = function(data) {
	    overlay_content.html(data);
	    var auto_area = overlay_content.find('#auto_change_group');
	    set_auto_complete(auto_area);
	    overlay_content.find('#change_group').click(function () {
		if (auto_area.css('display') == 'list-item') {
		    auto_area.hide();
		} else {
		    auto_area.show();
		}
		return false;
	    });
	    jq('#create_content').click(function (){
		var form = jq('#overlay_content form');
		var data = form.find(':input').serializeArray();
		jq.post(form.attr('action'), data, add_or_fail);
		return false;
	    });
	};
	initialize(data);
	var add_or_fail = function (data) {
	    if (data.indexOf('redirect:') !== -1) {
		window.location.href = data.split(':')[1];
	    } else {
		initialize(data);
	    }
	};
    });
};

var add_content = function () {
    jq('.add_content').overlay({expose: {
				   color:'#000000',
				   opacity:0.5
			       },
			       effect:'apple',
			       onLoad: function () {
				   get_add_content(this.getTrigger());
			       }
    });
};
var profile_ready = function () {
    add_content();
    wiki_edit();
    editing();
    setup_tag_lists();
    jq('#resources .add_tag, #resources .delete_tag, #resources .clear_tag, .pagination a').live('click', function () {
	jq('.tabbed_content #resources').load(jq(this).attr('href') + ' form');
	return false;
    });
    jq('.tabbed_content #resources #submit_search').live('click', function () {
	var form = jq(this).closest('form');
	jq('.tabbed_content #resources').load(form.attr('action') + ' form', form.serialize());
	return false;
    });
    if (jq('li.place .editable').length) {
	jq.getScript("http://maps.google.com/maps?file=api&v=2.x&key=ABQIAAAAiA7tLHdzZr8yhGAEbo5FGxS_srkAJTD0j5T3EF3o06M_52NTAhQM2w0ugG9dZdoyPl3s9RqydGrzpQ&async=2&callback=setup_maps");
    }
    //jq.getJSON('map_tags/', {}, init_rgraph);
};


