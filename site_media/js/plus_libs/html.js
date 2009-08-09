<!--

function expand(x,y) { return (x != "" ? " "+x+"='"+y+"' " : ""); }

function tag(name,x,y) { 
	if (typeof x == "string") {return "<"+name+">"+x+"</"+name+">";	}
	s = "<"+name;
	for (var i in x) { s+=expand(i,x[i]); }
	s += ">"+y+"</"+name+">";
	return s;
}

function td(x,y) { return tag("td",x,y); }
function table(x,y) { return tag("table",x,y); }
function tr(x,y) { return tag("tr",x,y); }
function div(x,y) { return tag("div",x,y); }
function h2(x,y) { return tag("h2",x,y); }
function h1(x,y) { return tag("h1",x,y); }
function p(x,y)  { return tag("p",x,y); }
function form(x,y)  {return tag("table",x,y); }
-->