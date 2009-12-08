var home = function () {
    var interval = null;
    var click_next = function (tab_container, no_tabs) {
	var active_index = tab_container.get('activeIndex');
	if (active_index == no_tabs-1) {
	    tab_container.set('activeIndex', 0);
	    clearInterval(interval);
	} else {
	    tab_container.set('activeIndex', active_index + 1);
	}
    };
    var tab_container = new YAHOO.widget.TabView('intro_bar_tabs');
    var no_tabs = tab_container.get('tabs').length;
    interval = setInterval(function () {
	click_next(tab_container, no_tabs);
    }, 7000);
};
