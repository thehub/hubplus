var initTabView = function (ele) {
    var tabView = new YAHOO.widget.TabView(ele.id);
    //tabView.addListener("activeTabChange", handleTabViewActiveTabChange);
};

var permission_ready = function () {
    var all_sliders = jq('#permission_sliders');
    initTabView(all_sliders.get(0));
    var Event = YAHOO.util.Event;
    var Dom   = YAHOO.util.Dom;
    var lang  = YAHOO.lang;
    var Y     = YAHOO.util.Selector;

    jq('.permission_button').overlay({expose: {
            color: '#BAD0DB',
            opacity: 0.7
        }});
    jq('.permission_button').click(function () {
	var resource_id= jq(this).attr('id').split('-')[1];
	var resource_class= jq(this).attr('id').split('-')[0];
	var load_url = "/permissions/edit/?current_id={resource_id}&current_class={resource_class}".supplant({'resource_id':resource_id, 'resource_class':resource_class});
	var change_slider = "/permissions/change_slider";
	var custom_default = "/permission/toggle_custom";
	jq.getJSON(load_url, function(json){
	    jq('#overlay_content').html(jq(json.html));
	    var sliders = json.sliders;
	    var agents = json.agents;
	    var custom = json.custom;
	    var create_slider_points = function (tbody) {
		var rows = tbody.find('tr').slice(1);
		var top_row = jq(rows[0]).offset().top;
		var heights = rows.map(function (i, row) {
		    var row = jq(row);
		    var row_top = row.offset().top - top_row;
		    var row_data = {'agent_id':row.attr('id').split('-')[1],'agent_class':row.attr('class').split()[1], middle:row_top + row.height()/2 - 6.5, 'top':row_top - 6.5, 'bottom':row_top + row.height() - 6.5};
		    row.data('slider', row_data);
		    return row_data;
		});
		return heights;
	    };
	    var setup_slider_group = function (i, ele) {
		var slider_group = jq(ele);
		var tbody = slider_group.find('tbody');
		var heights = create_slider_points(tbody);
		slider_group.find('.slider_holder').each( function (i, ele) {
		    var _interface = ele.id.split('-')[1];
		    var top = 0;
		    var top_cell = jq(ele).parent();
		    var bottom = tbody.height() - 13 - (jq(ele).parent().offset().top - tbody.offset().top);
		    var slider = YAHOO.widget.Slider.getVertSlider(ele.id, jq(ele).find('.slider').get(0), top, bottom);
		    slider.subscribe("change", function(offsetFromStart) {
			var s_cells = jq('.' + _interface);
			s_cells.each(function (i, cell) {
			    cell = jq(cell);
			    var row = cell.parent();
			    var row_data = row.data('slider');
			    if (offsetFromStart < row_data.bottom) {
				cell.addClass('active').removeClass('inactive');
			    } else {
				cell.addClass('inactive').removeClass('active');
			    }
			});
			return false;
		    });
		    slider.subscribe("slideEnd", function () {
			var offsetFromStart = slider.getValue();
			heights.each(function (i, row) {
			    if (offsetFromStart > row.top && offsetFromStart < row.bottom) {
				if (offsetFromStart != row.middle) {
				    slider.setValue(row.middle);
				}
			    };
			});
			return false;
		    });

		});
	    };
	    //if (custom) {
		// Pulling in the YUI libraries
		jq('.permissions_slider').each(setup_slider_group);
	    //}

        });
    });
};

/*

	slider.subscribe("change",function(offsetFromStart) {
		scaled = Math.round(scale(this.getValue()));
		slider_model.set_current(scaled);
		$('#scratch').html(sg.titles[slider_model.id] +
	                   " ("+slider_model.min+"), "+scaled+', '+sg.option_labels[scaled] );

		if (scaled != slider_model.get_current()) {
		    slider.setValue(scale.rev(slider_model.get_current()));
		}
	    });

	slider.callback = function(slider_model) {
	    // this lets the slider_model call us back to update constraints
	    $('#scratch2').html('model changed '+sg.titles[slider_model.id]+" min: "+slider_model.min);
	    this.update_position(slider_model);
	};

*/
