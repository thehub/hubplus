var widget_map = {'Profile':{'about':'text_wysiwyg'}
		 };

var init = function () {
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
	inplace_editor(element_id, 'field/' + object_prop + '/', {callback: function (form, val) {
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
            loadTextURL:  'field/' + object_prop + '/?default=' + encodeURIComponent(jq(ele).html())
	});
    });
};
jq(document).ready(function() {
    init();
});
