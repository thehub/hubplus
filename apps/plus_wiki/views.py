from django.conf import settings

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User

from django.template import RequestContext
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import models

from django.template import RequestContext
from apps.plus_groups.models import TgGroup
from apps.plus_permissions.api import secure_resource, TemplateSecureWrapper
from apps.plus_wiki.models import WikiPage



@login_required
@secure_resource(TgGroup)
def edit_wiki(request, group, page_name, template_name="plus_wiki/create_wiki.html"):
    try:
        secure_page = WikiPage.objects.plus_get(request.user, name=page_name, in_agent=group.get_ref())
    except WikiPage.DoesNotExist:
        raise Http404
    return render_to_response(template_name, 
                              {'page':TemplateSecureWrapper(secure_page),
                               'form_action':reverse("create_WikiPage", args=[secure_page.in_agent.obj.id, secure_page.name])}, 
                              context_instance=RequestContext(request))

    
@login_required
@secure_resource(TgGroup)
def create_wiki_page(request, group, page_name, template_name="plus_wiki/create_wiki.html"):
    try:
        obj = WikiPage.objects.plus_get(request.user, name=page_name, in_agent=group.get_ref())
    except:
        raise Http404

    title = request.POST.get('title', None)
    if title:
        obj.title = title
        obj.name_from_title()
    content = request.POST.get('content', None)
    if content:
        obj.content = content
    license = request.POST.get('license', None)
    if license:
        obj.license = license

    obj.stub = False
    obj.save()
    return HttpResponseRedirect(reverse('view_WikiPage', args=[group.id, obj.name]))


@login_required
@secure_resource(TgGroup)
def view_wiki_page(request, group, page_name, template_name="plus_wiki/wiki.html"):
    try:
        obj = WikiPage.objects.plus_get(request.user, name=page_name, in_agent=group.get_ref())
    except WikiPage.DoesNotExist:
        raise Http404
    return render_to_response(template_name, {'page':TemplateSecureWrapper(obj)}, context_instance=RequestContext(request))

@login_required
@secure_resource(TgGroup)
def delete_stub_page(request, group, page_name):
    try:
        obj = WikiPage.objects.plus_get(request.user, name=page_name, in_agent=group.get_ref(), stub=True)
        obj.delete()
    except WikiPage.DoesNotExist:
        pass
    return HttpResponseRedirect(reverse('group', args=[group.id]))
        
