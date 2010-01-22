var replace_file = function () {
    var upload_field = jq('.upload_field');
    upload_field.find('.keep_existing').click(function () {
	upload_field.find('.replace_file, .keep_existing').hide();
	upload_field.find('.replace_file_button, .file_name').show();
	return false;
    });
    upload_field.find('.replace_file_button').click(function () {
	upload_field.find('.replace_file, .keep_existing').show();
	upload_field.find('.replace_file_button, .file_name').hide();
	return false;
    });
};

var autocomplete_uploadable_groups = function() {
    var move_resource_list = jq('#move_resource');
    jq('.autocomplete_uploadable_groups').autocomplete('/groups/autocomplete/', {
            formatItem:function(item, i, max) {
                return item.display_name;
            },
            width: 175,
            matchSubset: false,
            selectFirst: true,
            max:10,
            dataType: 'json',
            parse: function(data) {
                var rows = new Array();
                for(var i=0; i<data.length; i++){
                    rows[i] = { data:data[i], value:data[i].id, result:data[i].display_name};
                }
                return rows;
	    }
	    }).result(function(event, data, formatted) {
			  //move_resource_list.find('#group_display_name').html(data.display_name);
			  move_resource_list.find('#new_parent_group').val(data.id);

            });

};
