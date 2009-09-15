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
	    var gutter = null;
	    myEditor = new YAHOO.widget.Editor(target.get(0), config);
	    myEditor._defaultToolbar.titlebar = false;
	    myEditor.on('toolbarLoaded', function() {
		YAHOO.log('Toolbar loaded, add button and create gutter', 'info', 'example');
		gutter = new YAHOO.gutter(myEditor);

		var flickrConfig = {
		    type: 'push',
		    label: 'Insert Flickr Image',
		    value: 'flickr'
		};

		myEditor.toolbar.addButtonToGroup(flickrConfig, 'insertitem');

		myEditor.toolbar.on('flickrClick', function(ev) {
		    YAHOO.log('flickrClick: ' + YAHOO.lang.dump(ev), 'info', 'example');
		    this._focusWindow();
		    if (ev && ev.img) {
			YAHOO.log('We have an image, insert it', 'info', 'example');
			//To abide by the Flickr TOS, we need to link back to the image that we just inserted
			var html = '<a href="' + ev.url + '"><img src="' + ev.img + '" title="' + ev.title + '"></a>';
			this.execCommand('inserthtml', html);
		    }
		    gutter.toggle();
		}, myEditor, true);
		gutter.createGutter();
		});
	    myEditor.render();
	    YAHOO.util.Event.on('page_edit_form', 'submit', function(e) {
		YAHOO.util.Event.stopEvent(e);
		myEditor.saveHTML();
		jq('#page_edit_form').submit();
	    });
	});


var Dom = YAHOO.util.Dom,
Event = YAHOO.util.Event;
    YAHOO.gutter = function(myEditor) {
        return {
            status: false,
            gutter: null,
            createGutter: function() {
                YAHOO.log('Creating gutter (#gutter1)', 'info', 'example');
                this.gutter = new YAHOO.widget.Overlay('gutter1', {
                    height: '425px',
                    width: '300px',
                    context: [myEditor.get('element_cont').get('element'), 'tl', 'tr'],
                    position: 'absolute',
                    visible: false
                });
                this.gutter.hideEvent.subscribe(function() {
                    myEditor.toolbar.deselectButton('flickr');
                    Dom.setStyle('gutter1', 'visibility', 'visible');
                    var anim = new YAHOO.util.Anim('gutter1', {
                        width: {
                            from: 300,
                            to: 0
                        },
                        opacity: {
                            from: 1,
                            to: 0
                        }
                    }, 1);
                    anim.onComplete.subscribe(function() {
                        Dom.setStyle('gutter1', 'visibility', 'hidden');
                    });
                    anim.animate();
                }, this, true);
                this.gutter.showEvent.subscribe(function() {
                    myEditor.toolbar.selectButton('flickr');
                    this.gutter.cfg.setProperty('context', [myEditor.get('element_cont').get('element'), 'tl', 'tr']);
                    Dom.setStyle(this.gutter.element, 'width', '0px');
                    var anim = new YAHOO.util.Anim('gutter1', {
                        width: {
                            from: 0,
                            to: 300
                        },
                        opacity: {
                            from: 0,
                            to: 1
                        }
                    }, 1);
                    anim.animate();
                }, this, true);
                var warn = '';
                if (myEditor.browser.webkit || myEditor.browser.opera) {
                    warn = myEditor.STR_IMAGE_COPY;
                }
                this.gutter.setBody('<h2>Flickr Image Search</h2><label for="flikr_search">Tag:</label><input type="text" value="" id="flickr_search"><div id="flickr_results"><p>Enter flickr tags into the box above, separated by commas. Be patient, this example my take a few seconds to get the images..</p></div>' + warn);
                this.gutter.render(document.body);
            },
            open: function() {
                Dom.get('flickr_search').value = '';
                YAHOO.log('Show Gutter', 'info', 'example');
                this.gutter.show();
                this.status = true;
            },
            close: function() {
                YAHOO.log('Close Gutter', 'info', 'example');
                this.gutter.hide();
                this.status = false;
            },
            toggle: function() {
                if (this.status) {
                    this.close();
                } else {
                    this.open();
                }
            }
        };
    };
YAHOO.util.Event.onAvailable('flickr_search', function() {
    YAHOO.log('onAvailable: #flickr_search', 'info', 'example');
    YAHOO.util.Event.on('flickr_results', 'mousedown', function(ev) {
        YAHOO.util.Event.stopEvent(ev);
        var tar = YAHOO.util.Event.getTarget(ev);
        if (tar.tagName.toLowerCase() == 'img') {
            if (tar.getAttribute('fullimage', 2)) {
                YAHOO.log('Found an image, insert it..', 'info', 'example');
                var img = tar.getAttribute('fullimage', 2),
                    title = tar.getAttribute('fulltitle'),
                    owner = tar.getAttribute('fullowner'),
                    url = tar.getAttribute('fullurl');
                this.toolbar.fireEvent('flickrClick', { type: 'flickrClick', img: img, title: title, owner: owner, url: url });
            }
        }
    }, myEditor, true);
    YAHOO.log('Create the Auto Complete Control', 'info', 'example');
    oACDS = new YAHOO.widget.DS_XHR("http://developer.yahoo.com/yui/examples/editor/assets/flickr_proxy.php",
        ["photo", "title", "id", "owner", "secret", "server"]);
    oACDS.scriptQueryParam = "tags";
    oACDS.responseType = YAHOO.widget.DS_XHR.TYPE_XML;
    oACDS.maxCacheEntries = 0;
    oACDS.scriptQueryAppend = "method=flickr.photos.search";

    // Instantiate AutoComplete
    oAutoComp = new YAHOO.widget.AutoComplete('flickr_search','flickr_results', oACDS);
    oAutoComp.autoHighlight = false;
    oAutoComp.alwaysShowContainer = true;
    oAutoComp.formatResult = function(oResultItem, sQuery) {
        // This was defined by the schema array of the data source
        var sTitle = oResultItem[0];
        var sId = oResultItem[1];
        var sOwner = oResultItem[2];
        var sSecret = oResultItem[3];
        var sServer = oResultItem[4];
        var urlPart = 'http:/'+'/static.flickr.com/' + sServer + '/' + sId + '_' + sSecret;
        var sUrl = urlPart + '_s.jpg';
        var lUrl = urlPart + '_m.jpg';
        var fUrl = 'http:/'+'/www.flickr.com/photos/' + sOwner + '/' + sId;
        var sMarkup = '<img src="' + sUrl + '" fullimage="' + lUrl + '" fulltitle="' + sTitle + '" fullid="' + sOwner + '" fullurl="' + fUrl + '" class="yui-ac-flickrImg" title="Click to add this image to the editor"><br>';
        return (sMarkup);
    };
});
}
};
