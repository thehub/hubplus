var listing_ready = function () {
    jq('.tabbed_content #resources form.order_list').submit(function () {
	var form = jq(this);
	jq('.tabbed_content #resources').load(form.attr('action') + ' form', form.serialize(), function () {
	    listing_ready();
	});
	return false;
    });
    var evt = jq.browser.msie ? "click" : "change";
    jq('.order_list li.sort select').bind(evt, function () {
	jq(this).closest('form').submit();
    });
};
