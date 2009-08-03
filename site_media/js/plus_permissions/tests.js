
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

function test_observer(target) {
    // creates fake object with a callback function which can act as an observer,
    // asserts that the object which calls it back is the same as the argument in this constructor.
    o = Object();
    o.flag = false;
    o.callback = function(other) {
	if (other===target) {
	    this.flag = true;
	}
    }
    return o;
}

function test_buffer(ut) {
    buffer = Buffer();
    ut.assertEquals('buffer1','',buffer._());
    buffer.add('a');
    ut.assertEquals('buffer2','a',buffer._());
    buffer.add('b');
    ut.assertEquals('buffer3','ab',buffer._());
    ut.assertEquals('buffer4','abc',buffer._('c'));
}
 			 
function test_higher_order(ut) {
    var xs=[1,2,3];
    ut.assertEqualArrays('ho1',[2,4,6],map(function(x){return x*2;},xs));
    comma_sep = joiner(',');
    ut.assertEquals('ho2','1,2,3',comma_sep(xs));
    no_sep = joiner('');
    ut.assertEquals('ho3','123',no_sep(xs));
}

function test_scaling(ut) {
    var scale = Transform(0,100,0,10,5);
    ut.assertEquals('scale 1',5,scale(50));
    ut.assertEquals('scale 2',10,scale(100));
    unscale = scale.rev;
    ut.assertEquals('scale 3',50,unscale(5));
    ut.assertEquals('scale 4',100,unscale(10));
}


function test_sliders(ut) {
    options = [['all',1,1],['members',1,2],['group',1,3],['me',2,1]];

    sm = SliderModel('test',options,0,0);

    ut.assertEquals('A','test',sm.get_title());
    ut.assertEquals(0,4,sm.options.length);
    ut.assertEquals(1,0,sm.current_idx);
    ut.assertEquals(2,'all',sm.get_current_label());
    ut.assertEquals(2.1,1,sm.get_current_content_type());
    ut.assertEquals(2.2,1,sm.get_current_id());
    sm.set_current_idx(1);
    ut.assertEquals(3,1,sm.current_idx);
    ut.assertEquals(4,'members',sm.get_current_label());
    ut.assertEquals(4.1,1,sm.get_current_content_type());
    ut.assertEquals(4.2,2,sm.get_current_id());

    ut.assertEqualArrays(4.5,['all','members','group','me'],sm.get_labels())

    ut.assertEquals(5,1,sm.get_current_idx());
    sm.set_current_idx(-1);
    ut.assertEquals(6,0,sm.get_current_idx());
    
    sm2 = SliderModel('test2',options,2,2);
    ut.assertEquals(7,2,sm2.get_current_idx());
    sm2.set_current_idx(3);
    ut.assertEquals(8,3,sm2.get_current_idx());
    sm2.set_current_idx(1);
    
    ut.assertEquals(9,2,sm2.get_current_idx());

    sm2.set_limit(1);
    sm2.set_current_idx(1);
    ut.assertEquals(10,1,sm2.get_current_idx());

    ut.assertFalse(sm2.has_observers());

    sm = SliderModel('read',options,0,0);
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

    ut.assertEquals(100,'Permissions',sg.title);

    ut.assertEquals(10.1,3,sg.get_width());
    ut.assertEquals(10.2,4,sg.get_length());

    ut.assertEquals(11,3,sg.sliders.length);    
    ut.assertEquals(12,2,sg.constraints.length);

    ut.assertEquals(13,'all',sg.get_label(0));
    ut.assertEquals(13.1,'me',sg.get_label(3));


    sm = sg.sliders[0];
    ut.assertTrue(14,sm.has_observers());

    sm2 = sg.sliders[1];
    ut.assertEquals(15,sm2,sm.get_observers()[0]);

    
    to = test_observer(sm);
    sm.add_observer(to);
    ut.assertEquals(15.5,3,sm.get_observers().length);

    sm.set_current_idx(2);

    ut.assertTrue(16,to.flag);
    ut.assertEquals(17,2,sm2.get_limit());

    sm.set_current_idx(3);
    ut.assertEquals(18,3,sm2.get_limit());

    html = sg.sliders_as_html('test_id',function(a,b,c) {});

    ut.assertEqualArrays(20,['read','write','execute'],sg.slider_titles_as_array());

    $('#element').html(html);

    //ut.assertStarts('xxxx',"<table class='permission_slider'><tr><th>",html);

    ut.report();

}


function test_all(dom_element) {
    ut = TestCase(writer);

    test_buffer(ut);
    test_higher_order(ut);
    test_scaling(ut);
    test_sliders(ut,dom_element);
}
