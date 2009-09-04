

var tab_history = function (container_id) {
    var tab_titles = [];
    jq('#' + container_id + ' .yui-nav li a').each(function(i, ele) {
        tab_titles[tab_titles.length] = jq(ele).attr('href').substr(1);
    });
    var bookmarkedTabViewState = YAHOO.util.History.getBookmarkedState("tabview");
    var initialTabViewState = bookmarkedTabViewState || "about";
    var tabView;
    YAHOO.util.History.register("tabview", initialTabViewState, function (state) {
	tabView.set("activeIndex",jq.inArray(state,  tab_titles));
    });
    function handleTabViewActiveTabChange (e) {
        var newState, currentState;
	newState = e.newValue._configs.href.value.substr(1);
        try {
            currentState = YAHOO.util.History.getCurrentState("tabview");
            if (newState != currentState) {
                YAHOO.util.History.navigate("tabview", newState);
            }
        } catch (e) {
	    tabView.set("activeIndex",jq.inArray(newState,  tab_titles));
        }
    }

    function initTabView (ele) {
        tabView = new YAHOO.widget.TabView(ele.id);
        tabView.addListener("activeTabChange", handleTabViewActiveTabChange);
    }
    YAHOO.util.History.onReady(function () {
        var currentState;
        jq('#' + container_id).each(function (i, ele) {
	    initTabView(ele);
        });
	currentState = YAHOO.util.History.getCurrentState("tabview");
	tabView.set("activeIndex",jq.inArray(currentState,  tab_titles));
    });
    try {
        YAHOO.util.History.initialize("yui-history-field", "yui-history-iframe");
    } catch (e) {
        initTabView(ele);
    }

};
