
function links(ele) {
    var manager = jq(ele);

    var target_id = manager.find('.target_id').val();
    var target_class = manager.find('.target_class').val();

    manager.find(".submit_link").click(function(e) {
	    var args = manager.find(':input').serializeArray();
	    console.log('args');
	    console.log(args);
	    jq.post( manager.find('.link_form').attr('target'), args, append_link);
	    return false;
	});
    var append_link = function() {
	console.log('back');
	manager.find('.list_of_links').append('<li><a href="'+'SOMEWHERE'+'">'+'MY LINK'+'</a></li>');
    }
}



var plus_links_ready = function () {
    jq('.external_links').each(function(i, ele) {
	    links(ele);
	});
};
