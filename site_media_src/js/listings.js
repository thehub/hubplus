var listing_ready = function () {
    jq('.tabbed_content #resources form.order_list').submit(function () {
	var form = jq(this); //.closest('form');
	jq('.tabbed_content #resources').load(form.attr('action') + ' form', form.serialize(), function () {
	    listing_ready();
	});
	return false;
    });
    var evt = jq.browser.msie ? "propertychange" : "change";
    jq('.order_list').bind(evt, function () {
	jq(this).submit();
	});
};