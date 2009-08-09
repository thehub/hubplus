
// Quick and dirty Unit Test framework to get up and running


var logs = [];

function writer(x) {
    logs.push('<p>'+x+'</p>');
}

function TestCase(report) {
    o = Object;
    o.count = 0;

    o.assertEquals = function(e,x,y) {
	if (x==y) { return true; }
	report("error "+e+" : expected "+x+" got "+y);
	this.count++;
	return false;
    }

    o.assertTrue = function(e,x) {
	if (x) { return true; }
	report("error "+ e);
	this.count++;
	return false;
    }
    
    
    o.assertFalse = function(e,x) {
	if (!x) { return true; }
	report("error "+e);
	this.count++;
	return false;
    }


    o.assertKey = function(e,d,k) {
	try {
	    x = d[k];
	    return true;
	} catch (e) {
	    report("error "+e+" no key "+k);
	    return false;
	}
    }

    o.assertNotKey = function(e,d,k) {
	try {
	    x = d[k];
	    report("error "+e+" has key "+k);
	    return false;
	} catch (e) {
	    return true;
	}
    }

    o.assertStarts = function(e,match,s) {
	if ( s.substr(0,match.length) == match) {
	    return true; 
	}
	report("error "+e + " (("+ s +")) doesn't start with ((" + match+ "))");
	this.count++;
	return false;
    }

    o.report = function() {
	if (this.count == 0) {
	    document.writeln('No errors');
	} else {
	    //debugger;
	    document.writeln('There are errors');
	    for (i=0;i<logs.length;i++) {
		document.writeln(logs[i]);
	    } 
	}	
    }

    
    o.equalArrays = function(array1, array2) {
	var temp = new Array();
	if ( (!array1[0]) || (!array2[0]) ) { // If either is not an array
	    return false;
	}
	if (array1.length != array2.length) {
	    return false;
	}
	// Put all the elements from array1 into a "tagged" array
	for (var i=0; i<array1.length; i++) {
	    key = (typeof array1[i]) + "~" + array1[i];
	    // Use "typeof" so a number 1 isn't equal to a string "1".
	    if (temp[key]) { temp[key]++; } else { temp[key] = 1; }
	    // temp[key] = # of occurrences of the value (so an element could appear multiple times)
	}
	// Go through array2 - if same tag missing in "tagged" array, not equal
	for (var i=0; i<array2.length; i++) {
	    key = (typeof array2[i]) + "~" + array2[i];
	    if (temp[key]) {
		if (temp[key] == 0) { return false; } else { temp[key]--; }
		// Subtract to keep track of # of appearances in array2
	    } else { // Key didn't appear in array1, arrays are not equal.
		return false;
	    }
	}
	// If we get to this point, then every generated key in array1 showed up the exact same
	// number of times in array2, so the arrays are equal.
	return true;
    }

    o.assertEqualArrays = function(e,xs,ys) {
	if (this.equalArrays(xs,ys)) { return true; }
	report("error "+e+", arrays " + xs + " and "+ ys +" are not equal");
	return false;
    }    

    return o;
}

function inspect_fields(x) {
    b='';
    for (var i in x) {
	b=b+', '+i;
    }
    return b;  
}
	
