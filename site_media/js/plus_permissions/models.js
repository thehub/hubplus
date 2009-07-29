

function SliderModel(title, labels, default_idx, min) {
    var o = Object();
    o.title = title;
    o.labels = labels;
    o.current_idx = default_idx;
    o.min = min;
    o.observers = [];

    o.get_length = function() {
	return this.labels.length;
    }

    o.get_title = function() {
        return this.title; 
    }

    o.get_current_label = function() {
	return this.labels[this.get_current_idx()];
    }

    o.set_current_idx = function(idx) {
	if (idx >= this.get_limit()) {
	    this.current_idx = idx;
	} else {
	    this.current_idx = this.get_limit();
        }
	this.changed();

    }

    o.get_current_idx = function() {
	return this.current_idx;
    }

    o.set_limit = function(limit) {
	this.min = limit;
	this.changed();
    }

    o.get_limit = function() { 
	return this.min;
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
		this.observers[i]['callback'];
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
	this.set_limit(other.get_current_idx());
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


function SliderGroup(json) {
    // json format is
    //{'title':'a title',
    // 'intro':'a description',
    // 'options':['options','on','the','sliders'],
    // 'sliders':['slider','names'],
    // 'current':[0,1,2], // current settings
    // 'mins':[0,0,0],    // minima for each slider
    // 'constraints':[[0,1],[0,2]] // pairs of dependencies, the second is constrained by the first

    // }

    var o = Object();
    o.title = json['title'];
    o.intro = json['intro'];
    o.sliders = [];
    
    for (var i=0;i<json['sliders'].length;i++) {
	o.sliders.push(SliderModel(json['sliders'][i],json['options'],json['current'][i],json['mins'][i]));
    }

    o.constraints = json['constraints'];
    for (var i=0;i<o.constraints.length;i++) {
        c = o.constraints[i];
	o.sliders[c[0]].add_observer(o.sliders[c[1]]);
    }
    o.Yahoo_sliders=[];

    o.slider_titles_as_array = function() {
	var titles = [];
	for (var i=0;i<this.sliders.length;i++) {
	    titles.push(this.sliders[i].title);
	}
	return titles;
    }

    o.get_width = function() {
	return this.sliders.length;
    }

    o.get_length = function() {
	return this.sliders[0].get_length();
    }

    o.slice = function(idx, label_col, is_first_row, make_slider_controller) {

	var td_active   = function(x) { return "<td class='setting active'>"+x+"</td>"; }
	var td_inactive = function(x) { return "<td class='setting inactive'>"+x+"</td>"; }

	var b=[label_col];
	for (var i=0;i<this.sliders.length;i++) {
	    slider = this.sliders[i];
	    bg_name = slider.title+"-bg";
	    slide_name = slider.title+"-slide";
	    if (is_first_row) {
		handle_img = "<img src='/site_media/images/slider_handle.gif' />";
		handle_div = div({'id':slide_name,'class':'yui-slider-thumb'},handle_img);
		slider_div = div({'id':bg_name,'class':'yui-v-slider','title':'Slider'},handle_div);
		if (make_slider_controller) {
		    Yahoo_slider = make_slider_controller(slider,slider.labels,bg_name,slide_name,slider.get_current_idx());
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
       
     
	titles = this.slider_titles_as_array();

	var th =function(x) { return "<th class='attribute_column'>"+x+"</th>"; }
	titles = "<th class='group_column'>Group</th>"+join(map(th,this.slider_titles_as_array()));

	if (this.sliders.length == 0) { 
	    t = table(tr(titles)); 
	} else {
	    b=[];
	    for (var i=0;i<this.sliders[0].labels.length;i++) {
		sl = this.slice(i,td({'class':'group_label'},this.sliders[0].labels[i]),i==0,make_slider_controller);
		b.push(join(sl));
	    }
	    t = table({'class':'permissions_slider','id':table_id},tr(titles)+join(map(tr,b)));
	}
	

	return div({'id':'permissions','class':'block'},join([header,intro,t]));
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

function Transform(from_low,from_hi,to_low,to_hi,to_step) {
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
