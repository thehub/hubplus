from django.http import HttpResponse


def one_model_field(request, object, fieldname, default='', form_class=None, inner_objects=None) :
    """This should be the generic "attribute" editor ... for any normal attribute, 
    this function lets use get its value, (with a default if it has none) or update it"""
    
    val = getattr(object, fieldname)
    if not request.POST:
        if not val:
            val = ""
        return HttpResponse("%s" % val, mimetype="text/plain")

    new_val = request.POST['value']

    if form_class :
        # there's a form, and there may be a validator, so use it
        try:
            field_validator = form_class.base_fields[fieldname]
            field_validator.clean(new_val)
        except ValidationError, e:
            return HttpResponse('%s' % e, status=500)

    try:
        setattr(object, fieldname, new_val)
        object.save()

        if inner_objects :
            # if some attributes of this object are, in fact, mere proxies for another object
            # then we must save that object too. Classic example : Profile and Users. Some Profile 
            # attributes now delegated to User
            for o in inner_objects :
                o.save()
    except Exception, e :
        return HttpResponse('%s' % e, status=500)
    new_val = new_val and new_val or default
    return HttpResponse("%s" % new_val, mimetype='text/plain')
