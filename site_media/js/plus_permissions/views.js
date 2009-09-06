var initTabView = function (ele) {
    var tabView = new YAHOO.widget.TabView(ele.id);
    //tabView.addListener("activeTabChange", handleTabViewActiveTabChange);
};

var permission_ready = function () {
    var all_sliders = jq('#permission_sliders');
    initTabView(all_sliders.get(0));
    jq('.permission_button').overlay({expose: {
					  color: '#000000',
					  opacity: 0.5
				      },
				      effect: 'apple',
				      onLoad: function () {
					  load_sliders(this.getTrigger());
				      }
    });
};

var load_sliders = function (perm_button) {
        var initialising = 0;
	jq('div.close').click(function () {
	    jq('#overlay_content').html("");
	});
	var resource_id = jq(perm_button).attr('id').split('-')[1];
	var resource_class= jq(perm_button).attr('id').split('-')[0];
	var load_url = "/permissions/edit/?current_id={resource_id}&current_class={resource_class}".supplant({'resource_id':resource_id, 'resource_class':resource_class});
	var change_slider = "/permissions/move/";
	var custom_default = "/permission/toggle_custom/";

	jq.getJSON(load_url, function(json){
	    jq('#overlay_content').html(json.html);
	    var sliders = {};
	    jq.each(json.sliders, function(index, slider_set){
		sliders[slider_set[0]] = slider_set[1];
		var interface_dict = {};
		jq.each(sliders[slider_set[0]]['interface_levels'], function(index, slider_levels) {
		    interface_dict[slider_levels[0]] = slider_levels[1];
		});
		sliders[slider_set[0]]['interface_levels'] = interface_dict;
	    });

	    var agents = json.agents;
	    var custom = json.custom;

	    var create_slider_points = function (tbody) {
		var rows = tbody.find('tr').slice(1);
		var top_row = jq(rows[0]).offset().top;
		var heights = rows.map(function (i, row) {
		    var row = jq(row);
		    var row_top = row.offset().top - top_row;
		    var row_data = {'agent_id':row.attr('id').split('-')[2],'agent_class':row.attr('id').split('-')[1], middle:row_top + row.height()/2 - 6.5, 'top':row_top - 6.5, 'bottom':row_top + row.height() - 6.5};
		    row.data('slider', row_data);
		    return row_data;
		});
		return heights;
	    };

	    var setup_slider_group = function (i, ele) {
		var slider_group = jq(ele);
		var obj_class = slider_group.attr('id').split('-')[0];
		var tbody = slider_group.find('tbody');
		var heights = create_slider_points(tbody);
		var interface_levels = sliders[obj_class]['interface_levels'];
		var constraints = sliders[obj_class]['constraints'];
		var interface_limits_map = {};
		var follow_position_map = {};

		slider_group.find('.slider_holder').each( function (i, ele) {
		    var slider_holder = jq(ele);
		    var _interface = ele.id.split('-')[1];
		    var top = 0;
		    var top_cell = jq(ele).parent();
		    var bottom = tbody.height() - 13 - (jq(ele).parent().offset().top - tbody.offset().top);
		    var slider = YAHOO.widget.Slider.getVertSlider(ele.id, jq(ele).find('.slider').get(0), top, bottom);
		    slider.animate = false;
		    var level_agent = interface_levels[_interface.split('_')[1]];
		    var slider_limits = {min:top, max:bottom, followers:[]};
		    var locked = 0;

		    var follow_position = function (position, iface, slideEnd) {
			//iface = iface.split('_')[1];
			var agent = interface_levels[_interface.split('_')[1]];
			var agent_row = jq('#agent-{class}-{id}'.supplant({'class':agent.classname, 'id':agent.id}));
			console.log(slideEnd);
			if (initialising==0 && position >= agent_row.data('slider').middle) {
			    if (!slideEnd) {
				locked = 1;
				console.log("set slider locked " + _interface.split('_')[1] + "when updated from " + iface + "with change");
			    } else {
				locked = 0;
				console.log("set slider unlocked " + _interface.split('_')[1] + "when updated from " + iface + "with slideEnd");
			    }
			    slider.setValue(position);

			}
			//change interface_levels here!
		    };

		    var initialize_limits = function () {
			var slider_constraints = constraints[_interface.split('_')[1]];
			if (!slider_constraints) {
			    return slider_limits;
			}
			slider_limits.min = 0;
			slider_limits.max = bottom;
			slider_limits.followers = [];
			jq.each(slider_constraints, function (i, constraint) {
			    if (constraint[1].indexOf('$') === 0) {
				var agent_row = jq('#agent-' + constraint[1].substring(1));
			    } else {
				var agent = interface_levels[constraint[1]];
				var agent_row = jq('#agent-{class}-{id}'.supplant({'class':agent.classname, 'id':agent.id}));
			    }
			    if (constraint[0] == '<=') {
				slider_limits.min = Math.max(slider_limits.min, agent_row.data('slider').top + 1);
			    } else if (constraint[0] == '<') {
				slider_limits.min = Math.max(slider_limits.min, agent_row.next().data('slider').top + 1);
			    } else if (constraint[0] == '>=') {
				if (!agent) {
				    slider_limits.max = Math.min(slider_limits.max, agent_row.data('slider').bottom - 1);
				} else {
				    slider_limits.followers[slider_limits.followers.length] = constraint[1];
				}
			    } else if (constraint[0] == '>' && !agent) {
				if (!agent) {
				    slider_limits.max = Math.min(slider_limits.max, agent_row.prev().data('slider').bottom - 1);
				}
				else {
				    slider_limits.followers[slider_limits.followers.length] = constraint[1];
				}
			    }
			    do_colouring(slider.getValue());
			});
			slider_holder.data('limits', slider_limits);
			var min = 0 - slider_limits.min;
			var max = slider_limits.max;
			slider.thumb.setYConstraint(min, max, 1);
			return slider_limits;
			// 
			// evaluate constraints transitively
			// on end_slide make all changes in 1 request - keep a registry of changes, wait for all to complete (each pops from a list and push a result to a list), when list empty while loop makes request

			// as move down by cell re-evalutate constraints, based on current positions


			// offsets for < constraint - one row down (hard)
		    };

		    var do_colouring = function (offsetFromStart) {
			var s_cells = jq('.' + _interface);
			s_cells.each(function (i, cell) {
			    cell = jq(cell);
			    var row = cell.parent();
			    var row_data = row.data('slider');
			    if (row_data.middle < slider_limits.min) {
				cell.removeClass('active inactive').addClass('limited_up');
			    } else if (row_data.middle > slider_limits.max) {
				cell.removeClass('active inactive').addClass('limited_down');
			    } else if (offsetFromStart < row_data.bottom) {
				cell.addClass('active').removeClass('inactive limited');
			    } else {
				cell.addClass('inactive').removeClass('active limited');
			    }
			});
		    };

		    interface_limits_map[_interface.split('_')[1]] = initialize_limits;
		    follow_position_map[_interface.split('_')[1]] = follow_position;
		    initialize_limits();
		    var row = jq('#agent-{class}-{id}'.supplant({'class':level_agent.classname, 'id':level_agent.id}));
		    slider.setValue(row.data('slider').middle);
		    initialising += 1;

		    slider.subscribe("change", function(offsetFromStart) {
			//should move dependent sliders here too
			jq.each(slider_limits.followers, function (i, iface) {
			    follow_position_map[iface](offsetFromStart, _interface);
			});
			do_colouring(offsetFromStart);
			return false;
		    });

		    var saved = function (json, status) {
			interface_levels[_interface.split('_')[1]] = {id:json.id, classname:json.classname};
			jq.each(slider_limits.followers, function (i, iface) {
				interface_limits_map[iface]();
			    }
			);
			//give user feedback! console.log(response);
		    };
		    slider.subscribe("slideEnd", function () {
			var offsetFromStart = slider.getValue();
			if (locked === 1) {
			    return false;
			}

			heights.each(function (i, row) {
			      if (offsetFromStart > row.top && offsetFromStart < row.bottom) {
				  var agent = interface_levels[_interface.split('_')[1]];
				  var agent_row = jq('#agent-{class}-{id}'.supplant({'class':agent.classname, 'id':agent.id}));
				  if (offsetFromStart != row.middle) {
				      slider.setValue(row.middle);
				  } else {
				      if (initialising == 0) {
					  console.log("here " + _interface);
					  jq.each(slider_limits.followers, function (i, iface) {
						      console.log("update interface" + iface);
					      follow_position_map[iface](offsetFromStart, _interface, true);
					  });
					//should set dependent sliders here and post their data too if changed.
					var iface = slider_holder.attr('id').split('-')[1].replace('_', '.');
					var slider_change = {};
					slider_change[iface] = [row.agent_class, row.agent_id];
					row.middle = offsetFromStart;
					jq.post(change_slider, {'current_id':resource_id, 'current_class':resource_class, 'json':JSON.stringify(slider_change)}, saved, 'json');
				    } else {
					initialising -= 1;
				    }
				}
			    }
			  }
			);
			return false;
		    });

		});
	    };
	    //if (custom) {
		// Pulling in the YUI libraries
		jq('.permissions_slider').each(setup_slider_group);
	    //}
        });
};
