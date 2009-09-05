from django.http import HttpResponse
from apps.plus_permissions.api import secure_resource


from apps.profiles.forms import ProfileForm, HostInfoForm
from apps.plus_groups.forms import TgGroupForm

# Form classes which validate fields
validation_mapping = {
    "Profile" : ProfileForm,
    "HostInfo" : HostInfoForm,
    "TgGroup" : TgGroupForm,
}


def inner_objects(x) :
    # Some object fields are proxies for another dependent class which also needs to be saved
    # eg. some Profile attributes are really User attributes and we must save the User object when we change them     
    # inner objects now takes an object and returns a function which returns a list of the inner objects    
    if x.__class__ == 'Profile' : 
        return [x.user]
    # we may add more here if there 
    return []

@secure_resource(obj_schema={'object':'any'})
def field(request, object, fieldname, default='') :
    """This should be the generic "attribute" editor ... for any normal attribute, 
    this function lets use get its value, (with a default if it has none) or update it"""
    
    val = getattr(object, fieldname)
    if not request.POST:
        if not val:
            val = ""
        return HttpResponse("%s" % val, mimetype="text/plain")

    new_val = request.POST['value']


    if validation_mapping.has_key(object.__class__.__name__) :
        # there's a form class which may validate this field
        try:
            form = validation_mapping(object.__class__.__name__)
            field_validator = form_class.base_fields[fieldname]
            field_validator.clean(new_val)
            new_val = form.cleaned_data[fieldname]
        except ValidationError, e:
            return HttpResponse('%s' % e, status=500)

    try:
        setattr(object, fieldname, new_val)
        object.save()

        if inner_objects.has_key :
            # if some attributes of this object are, in fact, mere proxies for another object
            # then we must save that object too. Classic example : Profile and Users. Some Profile 
            # attributes now delegated to User
            for o in inner_objects :
                o.save()
    except Exception, e :
        return HttpResponse('%s' % e, status=500)
    new_val = new_val and new_val or default
    return HttpResponse("%s" % new_val, mimetype='text/plain')
