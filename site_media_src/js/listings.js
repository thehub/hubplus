var listing_ready = function () {
    jq('.tabbed_content #resources form.order_list').live('submit', function () {
	var form = jq(this); //.closest('form');
	console.log(form.serialize())  ;
	jq('.tabbed_content #resources').load(form.attr('action') + ' form', form.serialize());
	return false;
    });
    jq('.order_list').live('change', function () {
	jq(this).submit();
	return false;
    });
};

