
	
(function() {
   var Event = YAHOO.util.Event;
    var Dom   = YAHOO.util.Dom;
    var lang  = YAHOO.lang;
    var Y     = YAHOO.util.Selector;


    var on_slider_model_changed = new YAHOO.util.CustomEvent('slider_model_change');
    
    var valuearea="slider-value", textfield="slider-converted-value";

    function setup_YUI_slider(slider_model, options, el_bg, el_thumb, init, step_size) {
	var no_options = options.length;
	var top = 0;
	var bottom = (20 * (no_options-1));
	var key_increment = 20;

	var slider = YAHOO.widget.Slider.getVertSlider(el_bg, el_thumb, top, bottom, step_size);

	var match = jq('#'+slider.id);
	
	slider.setValue(init);
	
	var scale = Transform(top,bottom,0,no_options-2,1);
		
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
	}

	
	slider.update_position = function(slider_model) {
	    slider.setValue(scale.rev(slider_model.get_current()));
	    // add colouring here
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


            sg = SliderGroup({'title':'Permissions',
		      'intro':'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut',
		      'option_labels':['all','members','group','me'],
		      'option_types':[1,1,1,2],
		      'option_ids':[1,2,3,1],
		      'sliders':['read','write','execute'],
		      'current':[0,3,3],
		      'mins':[0,0,0],
		      'constraints':[[0,1],[0,2]]
	});

	    h = sg.sliders_as_html('slider_group1',setup_YUI_slider);
            $('#inserted_table').html(h);

            sg.update_slider_ticks('slider_group1');
            
        });
    

})();