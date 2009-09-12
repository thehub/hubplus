from django.http import HttpResponse
from apps.plus_permissions.api import secure_resource
from django.forms import ValidationError
from apps.plus_groups.models import TgGroup
from apps.profiles.forms import ProfileForm, HostInfoForm
from apps.plus_groups.forms import TgGroupForm
from django.shortcuts import render_to_response, get_object_or_404


# Form classes which validate fields
validation_mapping = {
    "Profile" : ProfileForm,
    "HostInfo" : HostInfoForm,
    "TgGroup" : TgGroupForm,
}


def inner_objects(x) :
    # Some object fields are proxies for another dependent class which also needs to be saved
    # eg. some Profile attributes are really User attributes and we must save the User object when we change them     
    # inner objects now takes an object and returns a list of the inner objects    
    if x.get_inner_class().__name__ == 'Profile' : 
        return [x.user]
    # we may add more here if we find some
    return []

    


@secure_resource(obj_schema={'object':'any'})
def field(request, default='', **kwargs) :
    """This should be the generic "attribute" editor ... for any normal attribute, 
    this function lets us get its value, (with a default if it has none) or update it"""

    object = kwargs['object']
    fieldname = kwargs['fieldname']
    val = getattr(object, fieldname)

    if not request.POST:
        if not val:
            val = ""
        return HttpResponse("%s" % val, mimetype="text/plain")

    new_val = request.POST['value']


    if validation_mapping.has_key(object.get_inner_class().__name__) :
        # there's a form class which may validate this field
        try:
            try :
                form = validation_mapping[object.get_inner_class().__name__]
                field_validator = form.base_fields[fieldname]
                new_val = field_validator.clean(new_val)
            except Exception, e:
                print e
                import ipdb
                ipdb.set_trace()

        except ValidationError, e:
            return HttpResponse('%s' % e, status=500)

    try:
        setattr(object, fieldname, new_val)
        object.save()

        # if some attributes of this object are, in fact, mere proxies for another object
        # then we must save that object too. Classic example : Profile and Users. Some Profile 
        # attributes now delegated to User
        for o in inner_objects(object) :
                o.save()
    except Exception, e :
        return HttpResponse('%s' % e, status=500)
    new_val = new_val and new_val or default
    return HttpResponse("%s" % new_val, mimetype='text/plain')
