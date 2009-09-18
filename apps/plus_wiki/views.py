from django.conf import settings

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django.template import RequestContext
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import models

from django.template import RequestContext
from apps.plus_groups.models import TgGroup
from apps.plus_permissions.api import secure_resource, TemplateSecureWrapper
from apps.plus_wiki.models import WikiPage, VersionDelta
from apps.plus_wiki.forms import EditWikiForm
from reversion import revision
from reversion.models import Version
from datetime import datetime

@login_required
@secure_resource(TgGroup)
def edit_wiki(request, group, page_name, template_name="plus_wiki/create_wiki.html"):
    try:
        secure_page = WikiPage.objects.plus_get(request.user, name=page_name, in_agent=group.get_ref())
    except WikiPage.DoesNotExist:
        raise Http404
    contributors = get_contributors(request.user, secure_page)
    return render_to_response(template_name, 
                              {'page':TemplateSecureWrapper(secure_page),
                               'form_action':reverse("create_WikiPage", args=[secure_page.in_agent.obj.id, secure_page.name]),
                               'contributors':contributors}, 
                              context_instance=RequestContext(request))

@revision.create_on_success
@login_required
@secure_resource(TgGroup)
def create_wiki_page(request, group, page_name, template_name="plus_wiki/create_wiki.html"):
    """creates OR saves WikiPages
    """
    form = EditWikiForm(request.POST)
    try:
        obj = WikiPage.objects.plus_get(request.user, name=page_name, in_agent=group.get_ref())
    except:
        raise Http404

    if form.is_valid():
        title = form.cleaned_data['title']
        content = form.cleaned_data['content']
        license = form.cleaned_data['license']
        if request.POST.get('preview', None):
            return render_to_response(template_name, 
                                      {'page':TemplateSecureWrapper(obj),
                                       'data':form.data,
                                       'preview_content': content,
                                       'form_action':reverse("create_WikiPage", args=[obj.in_agent.obj.id, obj.name])}, 
                                      context_instance=RequestContext(request))
        else:
            revision.user = request.user
            revision.comment = form.cleaned_data['what_changed']
            revision.add_meta(VersionDelta, delta="change")
            if obj.stub: # we should change the "created_by" on the genericreference/permissions system to "owner"
                obj.created_by = request.user
            obj.title = title
            obj.name_from_title()
            obj.content = content
            obj.license = license
            obj.stub = False
            obj.save()
            return HttpResponseRedirect(reverse('view_WikiPage', args=[group.id, obj.name]))

    return render_to_response(template_name, 
                              {'page':TemplateSecureWrapper(obj),
                               'revision':revision,
                               'data':form.data,
                               'errors': form.errors,
                               'form_action':reverse("create_WikiPage", args=[obj.in_agent.obj.id, obj.name])}, 
                              context_instance=RequestContext(request))

def get_contributors(user, obj):
    """Get all users who have a revision on this object in their revision_set
    """
    content_type = ContentType.objects.get(model=obj._inner.__class__.__name__.lower())
    return User.objects.plus_filter(user, revision__version__object_id__exact=str(obj.id), revision__version__content_type=content_type, distinct=True)

from apps.plus_permissions.api import TemplateSecureWrapper

@login_required
@secure_resource(TgGroup)
def view_wiki_page(request, group, page_name, template_name="plus_wiki/wiki.html"):
    try:
        obj = WikiPage.objects.plus_get(request.user, name=page_name, in_agent=group.get_ref())
    except WikiPage.DoesNotExist:
        raise Http404
    version_list = Version.objects.get_for_object(obj._inner)
    version = Version.objects.get_for_date(obj._inner, datetime.now())
    contributors = get_contributors(request.user, obj)
    contributors = [TemplateSecureWrapper(contributor) for contributor in contributors]
    return render_to_response(template_name, {'page':TemplateSecureWrapper(obj), 'version':version, 'contributors':contributors}, context_instance=RequestContext(request))

@login_required
@secure_resource(TgGroup)
def delete_stub_page(request, group, page_name):
    try:
        obj = WikiPage.objects.plus_get(request.user, name=page_name, in_agent=group.get_ref(), stub=True)
        obj.delete()
    except WikiPage.DoesNotExist:
        pass
    return HttpResponseRedirect(reverse('group', args=[group.id]))
        
