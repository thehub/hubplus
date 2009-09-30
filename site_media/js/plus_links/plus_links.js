
function links(ele) {
    var manager = jq(ele);

    var target_id = manager.find('.target_id').val();
    var target_class = manager.find('.target_class').val();

    manager.find(".submit_link").click(function(e) {
	    var args = manager.find(':input').serializeArray();
	    jq.post( manager.find('.link_form').attr('target'), args, append_link);
	    return false;
	});
    var append_link = function(new_link) {
	manager.find(".list_of_links").append(new_link);
	manager.find(".link_form").toggle();
    }
 
    manager.find(".remove_link").each(function(i,e)  {
	    alert(e);
            jq(e).click(function(ev) { 
		    console.log(jq(e).attr('id'));
		    
		    var link = jq(e).parent().parent();
		    console.log(link);
		   
		    jq.get(jq(e).attr('id'), [], function(data) {
			    console.log(link);
			    
			    link.remove();
			}, "json");
		    return false;
	    });
	    //jq.get( manager.find('.remove_link').attr('href'), {'resource_id':}, remove_link);
	    return true;
	});

    var remove_link= function(id) {
	//manager.find("#links"+id).
    }


    manager.find(".link_form").toggle();
    manager.find(".show_link_form").click(function() { 
	    manager.find(".link_form").toggle();
	});


	
}



var plus_links_ready = function () {
    jq('.external_links').each(function(i, ele) {
	    links(ele);
	});
};
