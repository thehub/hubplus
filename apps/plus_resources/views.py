from __future__ import with_statement

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from apps.plus_resources.forms import UploadFileForm
from apps.plus_resources.models import Resource, get_or_create

from django.contrib.auth.decorators import login_required

from apps.plus_permissions.decorators import secure_resource

from apps.plus_groups.models import TgGroup
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.core.files import File

import os
    

def handle_uploaded_file(user, owner, form, f_data) :
    kwargs = dict([(k,v) for k,v in form.cleaned_data.iteritems()])

    resource = get_or_create(user, owner, **kwargs)
    resource.stub= False
    resource.save()



@login_required
@secure_resource(TgGroup)
def edit_resource(request, group, resource_name,  
                  template_name='plus_resources/upload.html', success_url=None, current_app="plus_groups", **kwargs) :

    try:
        secure_upload = Resource.objects.plus_get(request.user, name=resource_name, in_agent=group.get_ref())
    except Resource.DoesNotExist:
        raise Http404
 
    if not success_url :
        success_url = reverse(current_app + ':group',args=(group.id,))

    if request.POST :
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid() :
            handle_uploaded_file(request.user, group, form, request.FILES['resource'])
            return HttpResponseRedirect(success_url)
        else :
            print form.errors


    else :
        form = UploadFileForm()
        form.data['title'] = secure_upload.title
        form.data['name'] = secure_upload.name
    
    return render_to_response(template_name, {
        'form' : form,
        'page_title' : 'Upload a resource',
    }, context_instance=RequestContext(request, current_app=current_app))


@secure_resource(Resource)
def view_resource(request, resource) :
    import ipdb
    ipdb.set_trace()
