
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


function test_copy_dict(ut) {
    var d1, d2;
    d1 = {'a':1,'b':2,'c':3 };
    d2 = {};
    copy_dict(['a','b'],d1,d2);
    ut.assertEquals('copy_dict1',1,d2['a']);
    ut.assertEquals('copy_dict2',2,d2.b);
    ut.assertEquals('copy_dict3',undefined,d2['c']);
}
    

function test_slider(ut) {
    options = [['all',1,1],['members',1,2],['group',1,3],['me',2,1]];

    sm = SliderModel(987,0,0);

    ut.assertEquals(0.5,987,sm.id);

    ut.assertEquals(1,0,sm.get_current());

    sm.set_current(1);
    ut.assertEquals(3,1,sm.get_current());

    sm.set_current(-1);
    ut.assertEquals(6,0,sm.get_current());
    
    sm2 = SliderModel(4334,2,2);
    ut.assertEquals(7,2,sm2.get_current());
    sm2.set_current(3);
    ut.assertEquals(8,3,sm2.get_current());

    sm2.set_current(1);    
    ut.assertEquals(9,2,sm2.get_current());

    sm2.set_min(1);
    ut.assertEquals(99,1,sm2.min);

    sm2.set_current(1);
    ut.assertEquals(10,1,sm2.get_current());

    ut.assertFalse(101,sm2.has_observers());

    sm.set_min(0);
    sm.set_current(1);
    sm.set_min(2);
    ut.assertEquals(1101,2,sm.get_current());
}

function test_slider_group(ut,element){

    sg = SliderGroup({'title':'Permissions',
		      'intro':'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut',
		      'resource_id':456,
		      'resource_type':243,
		      'option_labels':['all','members','group','me'],
		      'option_types':[1,1,1,2],
		      'option_ids':[1,2,3,1],
		      'sliders':['read','write','execute'],
		      'interface_ids':['Class.Reader','Class.Writer','Class.Executor'],
		      'current':[0,3,3],
		      'mins':[0,0,0],
		      'constraints':[[0,1],[0,2]]
	});

    ut.assertEquals(100,'Permissions',sg.title);

    ut.assertEquals(101,456,sg.resource_id);
    ut.assertEquals(102,243,sg.resource_type);


    ut.assertEquals(110,3,sg.get_width());
    ut.assertEquals(111,4,sg.get_length());

    ut.assertEquals(115,3,sg.sliders.length);    
    ut.assertEquals(120,2,sg.constraints.length);
    ut.assertEquals(121,3,sg.interface_ids.length);

    ut.assertEquals(130,'all',sg.option_labels[0]);
    ut.assertEquals(131,'me',sg.option_labels[3]);

    sm = sg.sliders[0];
    ut.assertTrue(140,sm.has_observers());

    ut.assertEquals(145,sg,sm.get_observers()[0]);

    sm2 = sg.sliders[1];
    ut.assertEquals(150,sm2,sm.get_observers()[1]);
    
    to = test_observer(sm);
    sm.add_observer(to);
    ut.assertEquals(155,4,sm.get_observers().length);

    sm.set_current(2);

    ut.assertTrue(160,to.flag);
    
    ut.assertEquals(170,2,sm2.min);

    sm.set_current(3);
    ut.assertEquals(180,3,sm2.min);

    html = sg.sliders_as_html('test_id',function(a,b,c) {});

 
    ut.assertEqualArrays(200,['read','write','execute'],sg.titles);
  
    ut.assertEqualArrays(210,[1,1,1,2],sg.option_types);
    ut.assertEqualArrays(220,[1,2,3,1],sg.option_ids);
    ut.assertEquals(300,3,sg.get_current_option_id(0));
    ut.assertEquals(305,'me',sg.get_current_label(0));
    ut.assertEquals(310,2,sg.get_current_type(0));
    ut.assertEquals(320,1,sg.get_current_id(0));

    $('#element').html(html);

    //ut.assertStarts('xxxx',"<table class='permission_slider'><tr><th>",html);

    //json = sg.status_json();
    //alert(json);
    // should look like this :
    // {
    //	'read':{'interface_id':'Class.Reader','':},
    //	'write':{},
    //	'execute':{}
    // },sg.status_json());
    
    ut.report();

}


function test_all(dom_element) {
    ut = TestCase(writer);

    test_buffer(ut);
    test_higher_order(ut);
    test_scaling(ut);
    test_copy_dict(ut);
    test_slider(ut);
    test_slider_group(ut,dom_element);
}
