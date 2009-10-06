// functions used by pinax threadedcomments to create forms.
// may be moved elsewhere


function show_reply_form(comment_id, url, person_name) {

    // careful, next depends on structure of url given to us, 
    // we expect /comments/freecomment/CONTENT_TYPE/CONTENT_ID/FREECOMMENT_ID/
    xs = url.split('/');
    content_type_id = xs[3];
    content_id = xs[4];
    real_comment_id = xs[5];
    tail = [content_type_id, content_id, real_comment_id].join('/');
    var comment_reply = jq('#' + comment_id);
    var to_add = "";
    jq.get('/plus_comments/our_comment/'+tail+'/', 
	   function (data, textStatus) {
	       to_add = jq(data);
	       to_add.css("display", "none");
	       comment_reply.after(to_add);
	       to_add.slideDown(function() {
		       comment_reply.replaceWith(new Array('<a id="', 
						comment_id,'" href="javascript:hide_reply_form(\'',
						comment_id, '\',\'', url, '\',\'', person_name,
						'\')">Stop Replying</a>').join(''));
		   }); 
	  
	   });
}


function hide_reply_form(comment_id, url, person_name) {
    var comment_reply = jq('#' + comment_id);
    comment_reply.next().slideUp(function (){
	    comment_reply.next('.response').remove();
	    comment_reply.replaceWith(new Array('<a id="',
						comment_id,'" href="javascript:show_reply_form(\'', 
						comment_id, '\',\'', url, '\',\'', person_name,
						'\')">Reply</a>').join(''));
	});
}
