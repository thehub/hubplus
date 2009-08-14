from django.conf import settings

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import models

from django.template import RequestContext

from apps.plus_contacts.models import Application, PENDING, WAITING_USER_SIGNUP


 
# XXX temporary, ensure that the interface factory know about Application
from apps.plus_permissions.models import get_permission_system, PlusPermissionsNoAccessException
from apps.plus_permissions.Application import ApplicationViewer
get_permission_system().add_interface(Application,'Viewer',ApplicationViewer)



@login_required
def list_of_applications(request, template_name="plus_contacts/applicant_list.html"):
    if request.user.is_authenticated() :
        applications= Application.objects.filter(status=PENDING)
    else :
        HttpResponseRedirect()

    print applications

    return render_to_response(template_name, {
            'applications' : applications,
            }, context_instance=RequestContext(request))


@login_required
def accept_application(request,id) :
    application = Application.objects.get(id=id,permission_agent=request.user)
    print "AAA"
    try :
        ps = get_permission_system()
        # now approved ... we need to send a confirmation mail, however, for the moment, we'll just 
        # create the login url and show it,
        # also, if the applicant already has an account, we can join him/her to a group
        print "BBB"
        if application.is_site_application() :
            print "CCC"
            # contact is not a user 
            
            if ps.has_access(request.user,ps.get_site_members(),ps.get_interface_id("TgGroup","ManageMembers")) :
                print "Ccccc"
                # this user has permission to add contact to the site
                application.status = WAITING_USER_SIGNUP
                print "RRR %s" %application.status
                application.save()
                print "QQQ"
                url = application.generate_accept_url(request.user)
                print "PPP"
                # for the moment, we're just outputting the url to a page.
                # in fact, we'll mail this
                send_mail('Confirmation of account on Hub+', """Dear %s %s
                               We are delighted to confirm you have been accepted as a member of Hub+

                               Please visit the following link to confirm your account : %s
""" % (application.first_name, application.last_name, url), application.email_address,
                          [application.email_address], fail_silently=False)
                
                print "OOO"
                return render_to_response('plus_contacts/dummy_email.html',
                                          {'url':url},
                                          context_instance=RequestContext(request))
            else : 
                return render_to_response('no_permission.html', {
                        'msg' : "You don't have permission to accept this person into site_members ",
                        'user' : request.user,
                        'resource' : "the site-members group"
                        }, context_instance=RequestContext(request))
                

        # here, this user already exists, now we're going to allow to become member of group,
        # if we have the right permissions
        if application.requests_group() :
            # we're asking for a group
            print "DDD"
            try :
                application.group.accept_member(application.get_user())
                print "EEE"
                return HttpResponseRedirect(reverse('list_open_applications'))
            except PlusPermissionsNoAccessException :
                print "FFF"
                return render_to_response('no_permission.html', {
                        'msg' : "You don't have permission to accept this application into %" %application.group,
                        'user' : request.user,
                        'resource' : "an application you can't see"
                        }, context_instance=RequestContext(request))
                
            
        
        return HttpResponseRedirect(reverse('list_open_applications'))
    except PlusPermissionsNoAccessException :
        return render_to_response('no_permission.html', {
            'msg' : "You don't have permission to accept this application",
            'user' : request.user,
            'resource' : "an appl"
            }, context_instance=RequestContext(request))
    
    
