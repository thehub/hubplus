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
from django.db import transaction

from django.template import RequestContext

from apps.plus_contacts.models import Application, Contact
from apps.plus_contacts.status_codes import PENDING, ACCEPTED_PENDING_USER_SIGNUP, ACCEPTED
from apps.plus_contacts.forms import InviteForm

from apps.plus_permissions.interfaces import PlusPermissionsNoAccessException, secure_wrap
from apps.plus_permissions.api import site_context, secure_resource
from apps.plus_permissions.default_agents import get_all_members_group

from apps.plus_groups.models import TgGroup


@login_required
def list_of_applications(request, resource_id=None, template_name="plus_contacts/applicant_list.html", **kwargs):
    group = resource_id
    all_members_group = get_all_members_group()
    if group == None or int(group) == all_members_group.id:
        group = get_all_members_group()
        title = settings.SITE_NAME
        applications = Application.objects.plus_filter(request.user, status=PENDING, group=group, interface_names=['Viewer', 'Accept', 'Reject'], required_interfaces=['Viewer', 'Accept'], all_or_any='ALL')
    else:
        applications = Application.objects.plus_filter(request.user, status=PENDING, group=group, interface_names=['Viewer', 'Accept', 'Reject'], required_interfaces=['Viewer', 'Accept'], all_or_any='ALL')
        title = TgGroup.objects.get(id=group).get_display_name()

    reject = False
    
    if len(applications):
        app = applications[0]
        try:
            app.reject
            reject = True
        except PlusPermissionsNoAccessException:
            pass

    return render_to_response(template_name, {
            'title': title,
            'applications' : applications,
            'reject':reject
            }, context_instance=RequestContext(request))


@login_required
@transaction.commit_on_success
def accept_application(request, resource_id, id, **kwargs):
    application = Application.objects.plus_get(request.user, id=id, interface_names=['Viewer', 'Accept'])
    try:
        application.accept(request.user, request.get_host())
        return HttpResponseRedirect(reverse('plus_groups:list_open_applications', args=[application.group.id]))

    except PlusPermissionsNoAccessException :        
        sc = application.get_inner().get_security_context()
        return render_to_response('no_permission.html', {
                'msg' : _("You don't have permission to accept this application into %(group)s" %{'group':application.group}),
                'user' : request.user,
                'resource' : "an application you can't see"
                }, context_instance=RequestContext(request))


@login_required
@transaction.commit_on_success
def reject_application(request, resource_id, application_id, template_name="plus_contacts/applicant_list.html", **kwargs):
    application = Application.objects.plus_get(request.user, id=application_id, interface_names=['Viewer', 'Reject'])
    application.reject(request.user, request.get_host())
    return HttpResponseRedirect(reverse('plus_groups:list_open_applications', args=[application.group.id]))




@login_required
@site_context
def site_invite(request, site, template_name='plus_contacts/invite_non_member.html', **kwargs) :
    if request.POST:
        form = InviteForm(request.POST)

        if form.is_valid():
            form.clean()
            email_address = form.cleaned_data['email_address']
            if Contact.objects.filter(email_address=email_address):
             
                contact = Contact.objects.plus_get(request.user, email_address=email_address)
            else :
                username, first_name, last_name = split_name(form.cleaned_data['username'])
                # we don't really want to give "create_Contact" in general to this user
                # just convenient to have a contact now ... hence site.get_inner
                # XXX rethink this 
                contact = site.get_inner().create_Contact(request.user, 
                                    email_address = email_address, 
                                    first_name=first_name,
                                    last_name=last_name,
                                    status=ACCEPTED_PENDING_USER_SIGNUP)


            if form.cleaned_data['group'] :
                # XXX it's an invite to a hub ... 
                group = form.cleaned_data['group']
            else :
                group = None

            msg,url = contact.invite(site, request.user, request.get_host(), group=group)
            
            return render_to_response('plus_contacts/dummy_email.html',
                                          {'url':url, 'message':msg},                                      
                                          context_instance=RequestContext(request))

    else :
        form = InviteForm()
        
    return render_to_response(template_name, {
            'form':form,
            'hubs':TgGroup.objects.hubs(),
            }, context_instance=RequestContext(request))
                              

 
