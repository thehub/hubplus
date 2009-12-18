var listing_ready = function () {
    jq('.tabbed_content #resources form.order_list').submit(function () {
	var form = jq(this); //.closest('form');
	jq('.tabbed_content #resources').load(form.attr('action') + ' form', form.serialize(), function () {
	    listing_ready();
	});
	return false;
    });
    jq('.order_list li.sort select').change(function () {
	jq(this).submit();
    });
};
