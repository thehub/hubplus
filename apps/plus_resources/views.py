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
from apps.plus_resources.models import Resource, update_attributes
from apps.plus_groups.resources_common import MoveResourceForm


from django.contrib.auth.decorators import login_required

from apps.plus_permissions.decorators import secure_resource
from apps.plus_permissions.api import TemplateSecureWrapper, has_access, get_anon_user

from apps.plus_groups.models import TgGroup
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.core.files import File

from apps.plus_permissions.exceptions import PlusPermissionsNoAccessException

from apps.plus_wiki.models import WikiPage

import os

from apps.plus_lib.search import listing_args

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

    if secure_upload.name :
        old_name = secure_upload.name
    else :
        old_name = ''

    try:
        secure_upload.get_all_sliders
        perms_bool = True
    except PlusPermissionsNoAccessException:
        perms_bool = False

    if request.POST:
        post_kwargs = request.POST.copy()
        post_kwargs['obj'] = secure_upload

        if "delete_submit" in post_kwargs :
            if post_kwargs.has_key('delete_check') :
                secure_upload.delete()
                return HttpResponseRedirect(reverse(current_app + ':group', args=[group.id]))

        if "move_resource_submit" in post_kwargs :
            form = MoveResourceForm(post_kwargs)
            form.user = request.user # essential, user is checked inside form validation
            if form.is_valid() :
                new_parent_group = form.cleaned_data['new_parent_group']
                try :
                    secure_upload.move_to_new_group(new_parent_group)
                except Exception, e :
                    print e

                return HttpResponseRedirect(reverse(current_app + ':group', args=[form.cleaned_data['new_parent_group'].id]))

        form = UploadFileForm(post_kwargs, request.FILES, user=request.user)

        if form.is_valid():
            a_file = form.cleaned_data['resource']

            resource = update_attributes(secure_upload, request.user,
                                         title = form.cleaned_data['title'],
                                         name  = form.cleaned_data['name'],
                                         license = form.cleaned_data['license'],
                                         author = form.cleaned_data['author'],
                                         description = form.cleaned_data['description'],
                                         resource = a_file)
   
            resource.stub = False
            resource.in_agent = group.get_ref()

            # don't allow name to change as this affects the url
            if old_name :
                resource.name = old_name
            resource.save()
            
            if not success_url :
                success_url = reverse(current_app + ':view_Resource', args=(group.id, resource.name))
           
            from apps.plus_feed.models import FeedItem
            FeedItem.post_UPLOAD(request.user, resource)

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
        'resource':TemplateSecureWrapper(secure_upload), # let's us use resource_common included template
        'data' : form.data,
        'errors': form.errors,
        'form_action':'',
        'form_encoding':'enctype=multipart/form-data',
        'permissions':perms_bool,
        'tags':tags,
        'pages':[p.get_ref() for p in group.get_resources_of_class(WikiPage)],
        'pages_listings_args':listing_args('home', 'home', '')
        
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

