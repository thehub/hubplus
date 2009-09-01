#from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.utils.translation import ugettext

from django.contrib.admin.views.decorators import staff_member_required

from account.utils import get_default_redirect
from signup_codes.models import check_signup_code


from signup_codes.forms import SignupForm, InviteUserForm

from apps.plus_permissions.default_agents import get_admin_user, get_anon_user, get_site

from apps.plus_permissions.api import secure_resource
from apps.plus_permissions.proxy_hmac import hmac_proxy
from apps.plus_contacts.models import Application

def signup(request, form_class=SignupForm,
        template_name="account/signup.html", success_url=None):
    if success_url is None:
        success_url = get_default_redirect(request)
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            username, password = form.save()
            user = authenticate(username=username, password=password)
            
            signup_code = form.cleaned_data["signup_code"]
            signup_code.use(user)
            
            auth_login(request, user)
            request.user.message_set.create(
                message=ugettext("Successfully logged in as %(username)s.") % {
                'username': user.username
            })
            return HttpResponseRedirect(success_url)
    else:
        code = request.GET.get("code")
        #signup_code = check_signup_code(code)


        if signup_code:
            form = form_class(initial={"signup_code": code})
        else:
            if not settings.ACCOUNT_OPEN_SIGNUP:
                # if account signup is not open we want to fail when there is
                # no sign up code or what was provided failed.
                return render_to_response("signup_codes/failure.html", {
                    "code": code,
                }, context_instance=RequestContext(request))
            else:
                form = form_class()
    return render_to_response(template_name, {
        "form": form,
    }, context_instance=RequestContext(request))


@hmac_proxy
@secure_resource(Application)
def proxied_signup(request, application, form_class=SignupForm,
                   template_name="account/accepted_signup.html", success_url=None):
    # if we've got here, we already know that this function was called 
    # with request.user as the agent who's inviting / authorizing this new member
    # so we don't need to explicitly test.

    if success_url is None:
        success_url = get_default_redirect(request)


    # because this is a signup request that has an application object we, expect the application

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            application.applicant.become_member(username, accepted_by=request.user, password = password)
            user = authenticate(username=username, password=password)

            
            auth_login(request, user)
            user.message_set.create(
                message=ugettext("Successfully logged in as %(username)s.") % {
                'username': user.username
            })

            # Now, what happens if this application or invite came with a group?
            # If the group is not a Hub and the user has permissions on the group, then it's ok to add
            if application.group :
                if application.group.group_type != 'hub' :
                    group = secure_wrap(application.group, request.user)
                    group.add_member(user)
                else :
                    # but if the group *is* a hub, we need to do something over in Hubspace.
                    # So alert an appropriate admin
                    admins = application.group.get_admin_group().get_members()
                    from notification import models as notification
                    
                    for a in admin :
                        notification.send(admin, "new_application_for_hub", 
                            {'first_name':user.first_name,
                             'last_name':user.last_name,
                             'email_address':user.email_address,
                             'hub':group.display_name,
                       })
            

            application.delete()
            return HttpResponseRedirect(success_url)
    else:

        form = form_class()
        applicant = application.get_inner().applicant
        form.email_address = applicant.email_address


    # the outstanding issue is how to make sure that the form we're rendering comes back here
    # ie. with the hmac, let's pass it down as a "submit_url"

    # we must now get the original user (probably Anon) back ... otherwise it thinks we're
    # logged in as the proxy, which circumvents showing the signup form
    request.user = request.old_user         

    return render_to_response(template_name, {
        "form": form,
        "submit_url" : request.build_absolute_uri(),
        "display_name" : applicant.first_name + " " + applicant.last_name,
        
    }, context_instance=RequestContext(request))




#@staff_member_required - 
def admin_invite_user(request, form_class=InviteUserForm,
        template_name="signup_codes/admin_invite_user.html"):
    """
    This view, by default, works inside the Django admin.
    """

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.send_signup_code()
    else:
        form = form_class()
    return render_to_response(template_name, {
        "title": "Invite user",
        "form": form,
    }, context_instance=RequestContext(request))


