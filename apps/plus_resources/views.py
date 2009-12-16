from __future__ import with_statement

from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404

from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden,  Http404
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from apps.plus_resources.forms import UploadFileForm
from apps.plus_resources.models import Resource, get_or_create

from django.contrib.auth.decorators import login_required

from apps.plus_permissions.decorators import secure_resource
from apps.plus_permissions.api import TemplateSecureWrapper, has_access, get_anon_user

from apps.plus_groups.models import TgGroup
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.core.files import File

from apps.plus_permissions.exceptions import PlusPermissionsNoAccessException

import os
    

def handle_uploaded_file(user, owner, form, f_data) :
    kwargs = dict([(k,v) for k,v in form.cleaned_data.iteritems()])
    resource = get_or_create(user, owner, **kwargs)
    resource.stub = False
    resource.save()
    return resource

def change_parent(user, resource, new_parent, form) :
    if new_parent.has_interface('TgGroup.CreateResource') :
        current = secure_wrap(resource.in_agent.obj, user)
        

from apps.plus_tags.models import get_tags_for_object, tag_item_delete, TagItem

@login_required
@secure_resource(TgGroup)
def edit_resource(request, group, resource_name,  
                  template_name='plus_resources/upload.html', success_url=None, current_app="plus_groups", **kwargs) :

    if not group :
        raise Http404(_('This group does not exist'))
 
    try:
        secure_upload = Resource.objects.plus_get(request.user, name=resource_name, in_agent=group.get_ref())
    except Resource.DoesNotExist:
        raise Http404
 
    try:
        secure_upload.get_all_sliders
        perms_bool = True
    except PlusPermissionsNoAccessException:
        perms_bool = False

    if request.POST:
        post_kwargs = request.POST.copy()
        post_kwargs['obj'] = secure_upload
        form = UploadFileForm(post_kwargs, request.FILES, user=request.user)
        if form.is_valid():
            if form.cleaned_data['resource']:
                resource = handle_uploaded_file(request.user, group, form, form.cleaned_data['resource'])
            
            if form.cleaned_data['new_parent_group'] :
                change_parent(request.user, resource, form.cleaned_data['new_parent_group'], form)
            
            if not success_url :
                success_url = reverse(current_app + ':view_Resource', args=(group.id, secure_upload.name))

            return HttpResponseRedirect(success_url)
        else:
            pass

    else :
        form = UploadFileForm()
        form.data['title'] = secure_upload.title
        form.data['name'] = secure_upload.name
    
    tags = get_tags_for_object(secure_upload, request.user)

    return render_to_response(template_name, {
        'upload': TemplateSecureWrapper(secure_upload),
        'data' : form.data,
        'errors': form.errors,
        'form_action':'',
        'form_encoding':'enctype=multipart/form-data',
        'permissions':perms_bool,
        'tags':tags
    }, context_instance=RequestContext(request, current_app=current_app))
#'group_permissions_prototype': group.get_ref().permission_prototype


@secure_resource(TgGroup)
def view_resource(request, group, resource_name, template_name="plus_resources/view.html",
                   current_app='plus_groups', **kwargs):


    if not group :
        raise Http404(_('This group does not exist'))

    try:
        obj = Resource.objects.plus_get(request.user, name=resource_name, in_agent=group.get_ref())
    except Resource.DoesNotExist:
        raise Http404

    if not request.user.is_authenticated():
        request.user = get_anon_user()


    try:
        obj.get_all_sliders
        perms_bool = True
    except PlusPermissionsNoAccessException:
        perms_bool = False

    try :
        obj.comment
        can_comment=True
    except PlusPermissionsNoAccessException:
        can_comment=False

    edit = has_access(request.user, obj, 'Resource.Editor')
    tags = get_tags_for_object(obj, request.user)

    if obj.get_inner().created_by :
        created_by = obj.get_inner().created_by.get_display_name()
    else :
        created_by = None

    return render_to_response(template_name, {
        'upload' : TemplateSecureWrapper(obj),
        'page_title' : obj.title,
        'created_by' : created_by,
        'permissions' : perms_bool,
        'can_comment' : can_comment,
        'can_edit' : edit,
        'tags': tags
    }, context_instance=RequestContext(request, current_app=current_app))

@login_required
@secure_resource(TgGroup)
def delete_stub_resource(request, group, resource_name, current_app='plus_groups', **kwargs):
    try:
        obj = Resource.objects.plus_get(request.user, name=resource_name, in_agent=group.get_ref(), stub=True) 
        for tag_item in TagItem.objects.filter(ref=obj.get_ref()):
            tag_item_delete(tag_item)
        #check - delete gen_ref, perms, sec_context,
        obj.delete()
    except Resource.DoesNotExist:
        pass
    return HttpResponseRedirect(reverse(current_app + ':group', args=[group.id]))
