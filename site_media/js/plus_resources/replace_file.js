var replace_file = function () {
    var upload_field = jq('.upload_field');
    upload_field.find('.keep_existing').click(function () {
	upload_field.find('.replace_file, .keep_existing').hide();
	upload_field.find('.replace_file_button, .file_name').show();
    });
    upload_field.find('.replace_file_button').click(function () {
	upload_field.find('.replace_file, .keep_existing').show();
	upload_field.find('.replace_file_button, .file_name').hide();
    });
};
