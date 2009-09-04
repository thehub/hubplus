
function inspect_fields(x) {
    b='';
    for (var i in x) {
	b=b+', '+i;
    }
    return b;  
}
