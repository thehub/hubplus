

function SliderModel(id, init, min) {
    var o = Object();
    o.id = id;
    o.current = init;
    o.min = min;
    o.observers = [];

    o.get_current = function() {
	return this.current;
    }

    o.set_current = function(idx) {
	if (idx >= this.min) {
	    this.current = idx;
	} else {
	    this.current = this.min;
        }
	this.changed();
    }

    o.set_min = function(min) {
	this.min = min;
	if (this.current < this.min) { 
	    this.set_current(this.min);
	}
	this.changed();
    }


    o.has_observers = function() {
        return (this.observers.length > 0);
    }

    o.add_observer = function(ob) {
        this.observers.push(ob);
	this.changed();
    }

    o.get_observers = function() { 
        return this.observers;
    }

    o.changed = function() {
	for (var i=0;i<this.observers.length;i++) {
	    try {
		//this.observers[i]['callback'];
		this.observers[i].callback(this);
	    } catch (e) {
		// we don't care
	    }
	}
	if (this.Yahoo_slider) {
	    alert('we had a Yahoo slider');
	    this.Yahoo_slider.model_changed();
	}
    }
    
    o.callback = function(other) {
	this.set_min(other.get_current());
    }

    return o;
}

function map(f,xs) {
    ys = [];
    for (var i=0;i<xs.length;i++) {
	ys.push(f(xs[i]));
    }
    return ys;
}

function fold(f,xs,init) {
    var total=init;
    for (var i=0;i<xs.length;i++) {
	total=f(total,xs[i]);
    }
    return total;
}

function joiner(sep) {
    join=function(xs) {
	res = fold(function(s,i){return s+sep+i;},xs,'');
	if (sep=='') { return res; }
	return res.substr(1);
    }
    return join;
}


function copy_dict(keys,d1,d2) {
    // copy the elements with keys from d1 to d2
    for (var i=0;i<keys.length;i++) {
	d2[keys[i]]=d1[keys[i]];
    }

}

function SliderGroup(json) {
    // example json format is
    //  { 'title':'Permissions',
    //	  'intro':'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismt',
    //	  'resource_id':456,
    //	  'resource_type':243,
    //	  'option_labels':['all','members','group','me'],
    //	  'option_types':[1,1,1,2],
    //	  'option_ids':[1,2,3,1],
    //	  'sliders':['read','write','execute'],
    //	  'interface_ids':['Class.Reader','Class.Writer','Class.Executor'],
    //	  'current':[0,3,3],
    //	  'mins':[0,0,0],
    //	  'constraints':[[0,1],[0,2]]
    //  }
    var o = Object();

    copy_dict(['title','intro','option_labels','option_types','option_ids','interface_ids','resource_id','resource_type'],
	      json,o);
    o.titles = json['sliders'];
    
    o.sliders = [];    
    for (var i=0;i<json['sliders'].length;i++) {
	s=SliderModel(i,json['current'][i],json['mins'][i]);
	s.add_observer(o);
	o.sliders.push(s);
    }

    o.constraints = json['constraints'];
    for (var i=0;i<o.constraints.length;i++) {
        c = o.constraints[i];
	o.sliders[c[0]].add_observer(o.sliders[c[1]]);
    }    

    o.Yahoo_sliders=[];

    o.get_width = function() {
	return this.sliders.length;
    }

    o.get_length = function() {
	return this.option_labels.length;
    }

    o.new_current = function(json) {
	xs=json['current'];
	for (var i=0;i<xs.length;i++) {
	    this.sliders[i].set_current(xs[i]);
	}
    }

    o.slice = function(idx, label_col, is_first_row, make_slider_controller) {

	var td_active   = function(x) { return "<td class='setting active'>"+x+"</td>"; }
	var td_inactive = function(x) { return "<td class='setting inactive'>"+x+"</td>"; }

	var b=[label_col];
	for (var i=0;i<this.sliders.length;i++) {
	    slider = this.sliders[i];
	    bg_name = this.titles[i]+"-bg";
	    slide_name = this.titles[i]+"-slide";
	    if (is_first_row) {
		handle_img = "<img src='/site_media/images/slider_handle.gif' />";
		handle_div = div({'id':slide_name,'class':'yui-slider-thumb'},handle_img);
		slider_div = div({'id':bg_name,'class':'yui-v-slider','title':'Slider'},handle_div);
		if (make_slider_controller) {
		    Yahoo_slider = make_slider_controller(slider,this.option_labels,bg_name,slide_name,slider.get_current());
		    slider.add_observer(Yahoo_slider);
		    this.Yahoo_sliders.push( Yahoo_slider );

		}
	    } else {
		slider_div = '';
	    }
	    b.push(td_inactive(slider_div));
	}
	return b;
    }

    o.sliders_as_html = function(table_id, make_slider_controller) {

        join=joiner('');
	header = h2(this.title);
	intro = p(this.intro);
       
	var th =function(x) { return "<th class='attribute_column'>"+x+"</th>"; }
	titles = "<th class='group_column'>Group</th>"+join(map(th,this.titles));

	
	if (this.sliders.length == 0) { 
	    t = table(tr(titles)); 
	} else {
	    b=[];
	    for (var i=0;i<this.option_labels.length;i++) {
		sl = this.slice(i,td({'class':'group_label'},this.option_labels[i]),i==0,make_slider_controller);
		b.push(join(sl));
	    }
	    t = table({'class':'permissions_slider','id':table_id},tr(titles)+join(map(tr,b)));
	}
	submit = form({},'<input type="image" value="ok" class="submit" id="sliders_submit" src="/site_media/images/button_save.gif"/><input type="image" value="cancel" class="cancel" id="sliders_cancel" src="/site_media/images/button_cancel.gif"/>');

	return div({'id':'permissions','class':'block'},join([header,intro,t,submit]));
    }

    o.update_slider_ticks = function(table_id) {
	var table_height=$('#'+table_id).height();
	var thumb,height,step;
       
	for (var i=0;i<this.Yahoo_sliders.length;i++) {
	    slider = this.Yahoo_sliders[i];
	    thumb = slider.getThumb();
	    height = $('#'+table_id).height();
	    step = height / (this.get_length()+1);
	    thumb.setYConstraint(0,height,step);
	}
    }
    
   
    o.get_current_option_id = function(idx) {
	c = this.sliders[idx];
	return c.get_current();
    }

    o.get_current_label = function(idx) {
	c = this.sliders[idx];
	return this.option_labels[c.get_current()];
    }

    o.get_current_type = function(idx) {
	c = this.sliders[idx];
	return this.option_types[c.get_current()];
    }

    o.get_current_id = function(idx) {
	c = this.sliders[idx];
	return this.option_ids[c.get_current()];
    }

    o.callback = function(slider) {
	// now the SliderGroup observes all sliders. Maybe used to enforce constraints
    }

    o.get_as_json = function() {
	d = {'resource_type' : this.resource_type, 'resource_id' : this.resource_id};
	for (var i=0;i<this.sliders.length;i++) {
	    d[this.interface_ids[i]]= JSON.stringify([ this.get_current_type(i), this.get_current_id(i)]);
	}
	kills=[];
	for (var i=0;i<this.option_types.length;i++) {
	    kills.push([this.option_types[i],this.option_ids[i]]);
	}

	d['kill']=JSON.stringify(kills);
	return d;
    }


    return o;
}


function Buffer() {
    var o = Object();
    o.list = [];

    o.add = function(val) {
	this.list.push(val);
    }

    o._ = function(val) {
	if (val !== undefined) { this.add(val); }
	b = '';
	for (i=0;i<this.list.length;i++) {
	    b=b+this.list[i];
	}
	return b;
    }   
    return o;
}

function Transform(from_low, from_hi, to_low, to_hi) {
    f = function(x) {
	val = (x/(from_hi-from_low))*(to_hi-to_low);	
	return val;
    }
    f.rev = function(x) {
	val = (x/(to_hi-to_low))*(from_hi-from_low);	
	return val;
    }
    return f;
}
