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

from apps.plus_contacts.models import Application, Contact, PENDING, WAITING_USER_SIGNUP
from apps.plus_contacts.forms import InviteForm

from apps.plus_permissions.interfaces import PlusPermissionsNoAccessException
from apps.plus_permissions.api import site_context, secure_resource

from apps.plus_groups.models import TgGroup
from django.db import transaction

@login_required
def list_of_applications(request, template_name="plus_contacts/applicant_list.html"):
    applications= Application.objects.plus_filter(request.user, status=PENDING)        
    print applications
    return render_to_response(template_name, {
            'applications' : applications,
            }, context_instance=RequestContext(request))


@login_required
@transaction.commit_on_success
def accept_application(request,id) :
    application = Application.objects.plus_get(request.user, id=id)

    try :
        # now approved ... we need to send a confirmation mail, however, for the moment, we'll just 
        # create the login url and show it,
        # also, if the applicant already has an account, we can join him/her to a group

        if application.is_site_application() :
            # contact is not a user 

            msg,url = application.accept(request.user, request.get_host())
            print url
            return render_to_response('plus_contacts/dummy_email.html',
                                          {'url':url, 'message':msg},                                      
                                          context_instance=RequestContext(request))



        # here, this user already exists, now we're going to allow to become member of group,
        # if we have the right permissions
        if application.has_group_request() :
            # we're asking for a group

            try :
                application.group.accept_member(application.get_user())
            
                return HttpResponseRedirect(reverse('list_open_applications'))
            except PlusPermissionsNoAccessException :
            
                return render_to_response('no_permission.html', {
                        'msg' : _("You don't have permission to accept this application into %" %application.group),
                        'user' : request.user,
                        'resource' : "an application you can't see"
                        }, context_instance=RequestContext(request))

        
        return HttpResponseRedirect(reverse('list_open_applications'))
    except PlusPermissionsNoAccessException :
        
        sc = application.get_inner().get_security_context()
        return render_to_response('no_permission.html', {
            'msg' : _("You don't have permission to accept this application"),
            'user' : request.user,
            'resource' : _("an application that you can't accept"),
            'security_context' :sc.context_agent.obj,
            'tags' : sc.get_tags()
            }, context_instance=RequestContext(request))


def split_name(username):
    if username.find(' ') > 0 :
        first_name, last_name = (username.split(' ')) # note that if users need > 2 names, we have to do something
        username = '%s.%s' % (first_name,last_name)
    else : 
        first_name=username
        last_name = ''
    return username, first_name, last_name



@login_required
@site_context
def site_invite(request, site, template_name='plus_contacts/invite_non_member.html', **kwargs) :
    if request.POST:
        form = InviteForm(request.POST)

        if form.is_valid() :
            form.clean()
            email_address = form.cleaned_data['email_address']
            if Contact.objects.filter(email_address=email_address):
                print "We know this person as a contact"
                contact = Contact.objects.plus_get(request.user, email_address=email_address)
            else :
                print "New contact"
                username, first_name, last_name = split_name(form.cleaned_data['username'])
                # we don't really want to give "create_Contact" in general to this user
                # just convenient to have a contact now ... hence site.get_inner
                # XXX rethink this 
                contact = site.get_inner().create_Contact(request.user, 
                                    email_address = email_address, 
                                    first_name=first_name,
                                    last_name=last_name)


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
            }, context_instance=RequestContext(request))
                              

    
