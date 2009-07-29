
	
(function() {
    var Event = YAHOO.util.Event;
    var Dom   = YAHOO.util.Dom;
    var lang  = YAHOO.lang;
    var on_slider_model_changed = new YAHOO.util.CustomEvent('slider_model_change');
    
    var valuearea="slider-value", textfield="slider-converted-value";

    function setup_YUI_slider(slider_model, options, el_bg, el_thumb, init, step_size) {
	var no_options = options.length;
	var top = 0;
	var bottom = (20 * (no_options-1));
	var key_increment = 20;

	alert('fff');
	var slider = YAHOO.widget.Slider.getVertSlider(el_bg, el_thumb, top, bottom, step_size);
	alert('ggg '+slider);

	slider.setValue(init);
	
	var scale = Transform(top,bottom,0,no_options-2,1);
		
	slider.subscribe("change",function(offsetFromStart) { 
		scaled = Math.round(scale(this.getValue()));
		slider_model.set_current_idx(scaled);
		$('#scratch').html(slider_model.title + 
	                   "("+slider_model.get_limit()+"), "+scaled+","+slider_model.get_current_label());

		if (scaled != slider_model.get_current_idx()) {
		    slider.setValue(scale.rev(slider_model.get_current_idx()));
		}
	    });
	
	slider.callback = function(slider_model) {

	    // this lets the slider_model call us back to update constraints
	    $('#scratch2').html('model changed '+slider_model.title+" min: "+slider_model.get_limit());
	}

	slider.subscribe("slideStart", function() {
		YAHOO.log("slideStart fired", "warn");
	    });

	slider.subscribe("slideEnd", function() {
		YAHOO.log("slideEnd fired", "warn");
	    });

       	return slider;
    }
 
    
    Event.onDOMReady( function() {
	options = ['Public','Plus Members','Hub Islington Members','Tech Team','Me'];
	
	sg = SliderGroup('Permissions','Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut ',
	   [
	    SliderModel('Read',options,0,0),
	    SliderModel('Write',options,3,0),
	    SliderModel('Publish',options,3,0),
	    SliderModel('Manage',options,3,0),
	    SliderModel('Other',options,2,2)
	    ],[[0,1],[0,2]]);

	$('#inserted_table').html('Hello World');
	$('#inserted_table').html(sg.sliders_as_html('slider_group1',setup_YUI_slider));
	$('#inserted_table').html('Good Bye');
	sg.update_slider_ticks('slider_group1');


	});

})();