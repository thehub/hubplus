var wiki_edit = function () {
    if (jq('.wiki_edit').length) {
	var myEditor;
	jq('#content').each(function (i, ele){
	    var target = jq(ele).find('textarea');
	    var config = {
		height: target.height(),
		width: target.width(),
		dompath: true, //Turns on the bar at the bottom
		animate: true, //Animates the opening, closing and moving of Editor windows
		autoHeight: true
	    };
	    myEditor = new YAHOO.widget.Editor(target.get(0), config);
	    myEditor._defaultToolbar.titlebar = false;
	    myEditor.render();
	    jq('#page_edit_form').find('#edit_submit').one('click', function () {
		myEditor.saveHTML();
		jq('#page_edit_form').submit();
		return false;
	    });
	    jq('#page_edit_form').find('#preview').one('click', function () {
		myEditor.saveHTML();
		jq(this).click();
		return false;
	    });
	});
    }
};
