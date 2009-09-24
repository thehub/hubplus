from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from apps.plus_resources.forms import UploadFileForm
from apps.plus_resources.models import Resource, make_file_path

from django.contrib.auth.decorators import login_required

from apps.plus_permissions.decorators import secure_resource

from apps.plus_groups.models import TgGroup
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.core.files import File

import os

def make_full_save_path(owner_class, owner_id, resource_id) :
    return "%s/%s" % (settings.MEDIA_ROOT, make_file_path(owner_class, owner_id, resource_id))


def handle_uploaded_file(user, owner, form, f_data) :
    kwargs = dict([(k,v) for k,v in form.cleaned_data.iteritems()])

    # XXX change to this when permissions defined,
    # resource = owner.create_Resource(**kwargs)
    resource = Resource(owner=owner, title=kwargs['title'], description=kwargs['description'],
                        author=kwargs['author'], uploader=kwargs['uploader'], license=kwargs['license'],
                        resource=kwargs['resource'])
    resource.save()
    path= make_full_save_path(ContentType.objects.get_for_model(owner).model, owner.id, resource.id)

    try:
        os.makedirs(path)
    except Exception, e:
        print e
        # path probably exists

    # but we still have to save it manually, ourselves, try creating path manually
    f_name = "%s/%s"% (path, resource.resource.name)

    destination = open(f_name, 'wb+')
    for chunk in f_data.chunks():
        destination.write(chunk)
    destination.close()



# XXX generalize to more than group, but getting bogged down making that obj_schema thing work at the moment
@login_required
@secure_resource(TgGroup)
def upload_resource(request, group, template_name=None, success_url=None, **kwargs) :
    if not template_name :
        template_name = 'plus_resources/upload.html'
    if not success_url :
        success_url = reverse('group',args=(group.id,))
    if request.POST :
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid() :
            handle_uploaded_file(request.user, group, form, request.FILES['resource'])
            return HttpResponseRedirect(success_url)
        else :
            print form.errors
            import ipdb
            ipdb.set_trace()

    else :
        form = UploadFileForm()
        
    
    return render_to_response(template_name, {
        'form' : form,
        'page_title' : 'Upload a resource',
    }, context_instance=RequestContext(request))



