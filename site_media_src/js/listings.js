var listing_ready = function () {
    jq('.order_list').change(function () {
	jq(this).submit();
    });
};
