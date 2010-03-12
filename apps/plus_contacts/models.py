from django.db import models

from django.contrib.auth.models import User, UserManager

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from apps.plus_groups.models import TgGroup

from django.core.mail import send_mail

from django.conf import settings
from django.core.urlresolvers import reverse

from apps.plus_contacts.status_codes import PENDING, ACCEPTED_PENDING_USER_SIGNUP, ACCEPTED, REJECTED
from apps.plus_lib.models import extract 
from apps.plus_permissions.default_agents import get_site, get_all_members_group, get_admin_user

from apps.plus_permissions.types.User import create_user
from apps.plus_permissions.proxy_hmac import attach_hmac
import datetime

from django.db.models.signals import post_save

from django.template import Template, Context
from django.utils.translation import ugettext, ugettext_lazy as _

#from apps.plus_lib.countryfield import CountryField creates a circular import loop
CountryField = models.CharField

class Contact(models.Model):
    """Use this for the sign-up / invited sign-up process, provisional users"""
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email_address = models.CharField(max_length=255)  # unique=True) --> removing this requirement, I don't see why there can't be the same contact in more than user's contacts. Also it should be possible for a user to make more than one application e.g. to two different groups. We should then validate when creating users that the email address used isn't that of an existing user.
    organisation = models.CharField(max_length=255)
    address = models.CharField(null=True, max_length=300, default='') 
    country = CountryField(null=True, max_length=2, default='')
    post_or_zip = models.CharField(null=True, max_length=30, default="")
    find_out = models.TextField()
    
    has_accepted_application = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, related_name="user_contacts")

    def get_display_name(self):
        return self.first_name + " " + self.last_name

    def get_user(self):
        if self.user:
            return self.user
        else:
            try:
                user_match = User.objects.get(email_address=self.email_address)
                self.user = user_match
                self.save()
                return self.user
            except User.DoesNotExist:
                return None


    def become_member(self, username, invited_by=None, accepted_by=None, password=None):
        """Either a user accepts an invitation or their application is accepted.
        XXX If application is accepted trigger an email with confirmation page to set password
        XXX if invitation is accepted by user then they go straight to set password page
        """
        u = create_user(username, self.email_address)
        if password:
            u.set_password(password)
        p = u.get_profile()
        p.first_name = self.first_name if self.first_name else username
        p.last_name = self.last_name
        p.email_address = self.email_address
        p.organisation = self.organisation
        p.post_or_zip = self.post_or_zip
        p.address = self.address
        p.country = self.country

        if accepted_by:
            p.accepted_by = accepted_by
        h = p.get_host_info()
        h.find_out = self.find_out
        p.save()
        h.save()

        u.is_active = True
        u.save()
        
        self.user = u
        self.save()
        self.update_applications()
        self.update_invitations()
        for contact in Contact.objects.filter(email_address=self.email_address):
            contact.user = u
            contact.update_applications()
            contact.update_invitations()
        other_groups = u.groups.exclude(id=get_all_members_group().id) 
 
        if other_groups.count()==1:
            u.homehub = other_groups[0]
        else:
            u.homehub = get_all_members_group()
        
        return u


    def update_invitations(self):
        pass

    def update_applications(self):
        # pending applications should have their "applicant" changed from this contact to the newly created user 
        # e.g. if the "contact" has applied to join a group/hub and this hasn't yet been accepted/rejected
        for application in Application.objects.filter(applicant_object_id=self.id, 
                                                      applicant_content_type=ContentType.objects.get_for_model(Contact),
                                                      status=PENDING):            
            application.applicant = self.user
            application.save()

        
        # add the user to the groups where the contact has been accepted
        # e.g. if a host is accepting a site-application this will include the site_members_group 
        for application in Application.objects.filter(applicant_object_id=self.id, 
                                                      applicant_content_type=ContentType.objects.get_for_model(Contact),
                                                      status=ACCEPTED_PENDING_USER_SIGNUP):
            application.applicant = self.user
            group = application.group
            application.status = ACCEPTED
            group.join(self.user)
            application.save()
        

    def make_signup_link(self, sponsor, id) :
        url = attach_hmac("/account/signup/%s/" % id, sponsor)
        return 'http://%s%s' % (settings.DOMAIN_NAME, url)

    def make_accept_invite_link(self, sponsor, id) :
        url = attach_hmac("/invites/accept/%s/" % id, sponsor)
        return 'http://%s%s' % (settings.DOMAIN_NAME, url)

    def send_link_email(self, title, message, sponsor, id) :
        url = self.make_signup_link(sponsor, id)
        message = message + _("""

Please visit the following link to confirm your account : %(url)s""") % {'url': url}

        send_mail(title, message, settings.CONTACT_EMAIL,
                  [self.email_address], fail_silently=True)
        return message, url

    def accept_mail(self, sponsor, site_root, application_id):
        message = _("""
Dear %(first)s %(last)s
We are delighted to confirm you have been accepted as a member of %(site)s
""") % {'first':self.first_name, 'last':self.last_name, 'site':settings.SITE_NAME}

        return self.send_link_email(_("Confirmation of account on %(site)s") % {'site':settings.SITE_NAME}, message, sponsor, application_id)


    def message(self, sender, subject, body) :

        if self.get_user() :
            return self.get_user().message(sender, subject, body)
        else :
            from messages.models import Message
            from django.core.mail import send_mail
            message = _("""

%(sender)s has sent you a new message from %(site_name)s .

%(body)s

""") % {'site_name':settings.SITE_NAME, 'body':body,  'sender':sender.get_display_name()}

            send_mail(subject, message, settings.SUPPORT_EMAIL, [self.email_address],fail_silently=True)
            return False


    def group_invite_message(self, group, invited_by, accept_invite_url, special_message) :
        
        message = Template(settings.CONTACT_GROUP_INVITE_TEMPLATE).render(
            Context({'sponsor':invited_by.get_display_name(),
                     'first_name':self.first_name,
                     'last_name':self.last_name,
                     'signup_link':accept_invite_url,
                     'group_name':group.get_display_name(),
                     'site_name':settings.SITE_NAME,
                     'special_message':special_message,
                     }))
        message = message + """  
%s """ % accept_invite_url
        subject = Template(settings.GROUP_INVITE_SUBJECT_TEMPLATE).render(
            Context({'group_name':group.get_display_name() }))
        return self.message(invited_by, subject, message)


class Application(models.Model):
    """This should move to plus_groups
    """
    applicant_content_type = models.ForeignKey(ContentType, related_name='applicant_type')
    applicant_object_id = models.PositiveIntegerField()
    applicant = generic.GenericForeignKey('applicant_content_type', 'applicant_object_id') # either user or contact
    
    group = models.ForeignKey(TgGroup, null=True) #should change to False
    request = models.TextField()
    status = models.PositiveIntegerField(default=PENDING)

    admin_comment = models.TextField(default='')
    date = models.DateField(auto_now_add=True)
    accepted_by = models.ForeignKey(User, null=True, related_name="accepted_applications")
    rejected_by = models.ForeignKey(User, null=True, related_name="rejected_applications")

    def is_site_application(self):
        """ Is this an application by someone who's not yet a site-member and needs an User / Profile object created"""

        if isinstance(self.applicant, Contact) and not self.applicant.get_user():
            return True
        return False

    def accept(self, sponsor, site_root, **kwargs):
        if self.is_site_application():
            #applicant is a contact
            self.status = ACCEPTED_PENDING_USER_SIGNUP
            #self.applicant.save()  # wot?
        else:
            self.status = ACCEPTED
            self.group.join(self.applicant)

        if kwargs.has_key('admin_comment'):
            self.admin_comment = kwargs['admin_comment']

        self.accepted_by = sponsor
        self.save()
        #send and email if the application is a site application and contact hasn't yet been ACCEPTED through another application
        if self.is_site_application():
            if not self.applicant.has_accepted_application:
                self.applicant.accept_mail(sponsor, site_root, self.id)
                self.applicant.has_accepted_application = True
                self.applicant.save()

            all_members_group = get_all_members_group()
            #if this isn't an application to the site_members_group, find the application to the all_members_group and change its status to ACCEPTED_PENDING_USER_SIGNUP.
            if self.group.id != all_members_group.id:
                try:
                    site_app = Application.objects.get(applicant_object_id=self.applicant.id, 
                                                       applicant_content_type=ContentType.objects.get_for_model(Contact), 
                                                       status=PENDING, 
                                                       group=all_members_group)
                    site_app.accept(sponsor, site_app, **kwargs)
                except Application.DoesNotExist:
                    pass
        return True

    def reject(self, user, site_root):
        self.rejected_by = user
        if self.is_site_application():
            subject = _("Your application to %(site_root)s was declined") % {'site_root':site_root}

            data = {'group_name':site_root,
                    'rejected_by': self.rejected_by.get_display_name(),
                    'applicant':self.applicant.get_display_name()}

            context = Context(data)
            msg = Template(settings.APPLICATION_REJECT_TEMPLATE).render(context)

            send_mail(subject, msg, settings.CONTACT_EMAIL,
                      [self.applicant.email_address], fail_silently=False)
        self.status = REJECTED
        self.save()


    def get_approvers(self):
        return self.group.get_admin_group().get_users()


    def __str__(self):
        return u"<Application from %s, %s, (group %s)" % ('%s %s'% (self.applicant.first_name,self.applicant.last_name),self.request,self.group) 



def create_messages(sender, instance, **kwargs):


    if instance is None:
        return
    application = instance
    if application.status == PENDING:
        approvers = instance.get_approvers()
        for approver in approvers:
            if isinstance(application.applicant, User):
                sender = application.applicant
            else:
                sender = get_admin_user()

            review_url = 'http://' + settings.DOMAIN_NAME + reverse('plus_groups:list_open_applications', args=[application.group.id])

            if application.group.id == get_all_members_group().id:
                group_name = settings.SITE_NAME.encode('utf-8')
            else:    
                group_name = application.group.get_display_name()

            find_out = ""
            if isinstance(application.applicant, Contact):
                find_out = application.applicant.find_out
            context = Context({'first_name':application.applicant.first_name,
                               'last_name':application.applicant.last_name,
                               'email_address':application.applicant.email_address,
                               'organisation':application.applicant.organisation,
                               'group_name':group_name,
                               'request':application.request,
                               'review_url':review_url,
                               'find_out':find_out})

            msg = Template(settings.APPLICATION_MESSAGE).render(context)
            approver.message(sender=sender, 
                         subject="Application to %s from %s" %(group_name, application.applicant.get_display_name()), 
                         body=msg)

    #if the application has a user then we want to message them
    if not application.is_site_application():
        if application.status == ACCEPTED:
            group = application.group
            accepted_by = application.accepted_by
            applicant = application.applicant
            data = {'group_name':group.get_display_name(),
                    'accepted_by': accepted_by.get_display_name(),
                    'applicant':applicant.get_display_name(),
                    'group_url':reverse('plus_groups:group', args=[group.id])}

            msg = settings.ACCEPTED_TO_GROUP % data
            
            applicant.message(sender=accepted_by,
                         subject="Your application to %(group_name)s was accepted" % data,
                         body=msg)

        elif application.status == REJECTED:
            group = application.group
            rejected_by = application.rejected_by
            applicant = application.applicant
            data = {'group_name':group.get_display_name(),
                    'rejected_by': rejected_by.get_display_name(),
                    'applicant':applicant.get_display_name(),
                    'group_url':reverse('plus_groups:group', args=[group.id])}

            context = Context(data)
            msg = Template(settings.APPLICATION_REJECT_TEMPLATE).render(context)

            applicant.message(sender=rejected_by,
                         subject="Your application to %(group_name)s was declined" % data,
                         body=msg)


if "messages" in settings.INSTALLED_APPS:
    post_save.connect(create_messages, sender=Application, dispatch_uid="apps.plus_contacts.models")
