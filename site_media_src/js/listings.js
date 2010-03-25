
var listing_ready = function () {

    jq('.tabbed_content .page_content form.order_list').submit(function () {
	    var form = jq(this);
	    var tab = jq(this).parents('.page_content');
	    tab.load(form.attr('action') + ' form', form.serialize(), function () {
	    listing_ready();
	});
	return false;
    });
    jq('.order_list li.sort select').change(function () {
	jq(this).closest('form').submit();
    });
};

