
function permission_ready() {


    el_sliders = jq('#permission_sliders');

    // setting up click on the "edit" button

    jq('#permission_button').click(
        function() { 
	    // Get the resource id,
	    //jq('#resource_id') ...
            var resource_id='phil'; // CHANGE

	    var load_url = "/profiles/"+resource_id+"/get_main_permission_sliders/";
	    var post_url = "/profiles/"+resource_id+"/update_main_permission_sliders/";

	    v = $.getJSON(load_url,function(json){
		    sg = SliderGroup(json['sliders']);
		    h = sg.sliders_as_html('slider_group1', setup_YUI_slider);
		    el_sliders.html(h);
		    sg.update_slider_ticks('slider_group1');

	            // submit
	            el_sliders.find('#sliders_submit').one('click',function() {
			ajax_submit();
		       
		    });
		
	            // cancel
	            el_sliders.find('#sliders_cancel').one('click',function() {
		       el_sliders.html('');
		    });
		
            
                    function ajax_submit() {			
			var xhr = jq.ajax({
			   type: 'post',
                           url: post_url,
			   data: sg.get_as_json(),
                           success: function (response) { 
				    el_sliders.html('');
			   },
                           error: function(response) {alert('failure'); }
			});

		    }
		    
		    
		});

          
	});


    // Pulling in the YUI libraries 
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


};