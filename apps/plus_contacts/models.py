from django.db import models

from django.contrib.auth.models import User, UserManager
from django.contrib.contenttypes.models import ContentType

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from apps.plus_groups.models import TgGroup

from django.core.mail import send_mail

from django.conf import settings

from apps.plus_contacts.status_codes import PENDING, WAITING_USER_SIGNUP
from apps.plus_lib.models import extract 
from apps.plus_permissions.default_agents import get_site, get_all_members_group

from apps.plus_permissions.types.User import create_user
from apps.plus_permissions.proxy_hmac import attach_hmac
import datetime

from django.db.models.signals import post_save



class Contact(models.Model):
    """Use this for the sign-up / invited sign-up process, provisional users"""
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    organisation = models.CharField(max_length=255)
    email_address = models.CharField(max_length=255,unique=True)
    location = models.CharField(max_length=100)
    apply_msg = models.TextField()
    find_out = models.TextField()
    invited_by = models.ForeignKey(User,null=True,related_name='invited_contact')


    def get_user(self) :
        if len( User.objects.filter(email_address=self.email_address) ) < 1 : 
            return None
        return User.objects.get(email_address=self.email_address)

    def become_member(self, username, invited_by=None, accepted_by=None, password=None):
        """Either a user accepts an invitation or their application is accepted.
        XXX If application is accepted trigger an email with confirmation page to set password
        XXX if invitation is accepted by user then they go straight to set password page
        """
        u = create_user(username, self.email_address)
        if password:
            u.set_password(password)
        u.save()
        p = u.get_profile()
        p.first_name = self.first_name
        p.last_name = self.last_name
        p.email_address = self.email_address
        p.organisation = self.organisation
        p.location = self.location
        if invited_by:
            p.invited_by = invited_by
        if accepted_by:
            p.accepted_by = accepted_by
        h = p.get_host_info()
        h.find_out = self.find_out
        p.save()
        h.save()

        get_all_members_group().add_member(u)

        # do we want to delete the Contact if it becomes a User?
        
        # yes if this is merely a pending user, 
        # no if it's going to grow into a more sophisticated CRM system
        # self.delete()
        
        return u


    def send_link_email(self, title, message, sponsor, site_root, id):
        url = attach_hmac("/signup/%s/" % id, sponsor)
        url = 'http://%s%s' % (site_root, url)

        message = message + """

Please visit the following link to confirm your account : %s""" % url

        try :

            send_mail(title, message, settings.CONTACT_EMAIL,
                  [self.email_address], fail_silently=False)
            print "Email sent to %s" % self.email_address
        except Exception, e :
            print settings.EMAIL_HOST, settings.EMAIL_PORT
            print e

        return message, url


    def accept_mail(self, sponsor, site_root, application_id):
        message = """
Dear %s %s
We are delighted to confirm you have been accepted as a member of MHPSS
""" % (self.first_name, self.last_name)
        return self.send_link_email("Confirmation of account on MHPSS", message, sponsor, site_root, application_id)

    def invite_mail(self, sponsor, site_root, application_id) :
        message = """
Dear %s %s,
%s has invited you to become a member of MHPSS... MORE TEXT HERE""" % (self.first_name, self.last_name, sponsor.display_name)
        return self.send_link_email("Invite to join MHPSS", message, sponsor, site_root, application_id)



    def invite(self, site, sponsor, site_root, group=None):
        # this called on a contact if someone is inviting them to join the site
        application = site.create_Application(sponsor, applicant=self)
        if group :
            # this is an invitation, probably to a hub
            application.group=group
        return self.invite_mail(sponsor, site_root, application.id)
        
class Application(models.Model) :
    applicant_content_type = models.ForeignKey(ContentType,related_name='applicant_type')
    applicant_object_id = models.PositiveIntegerField()
    applicant = generic.GenericForeignKey('applicant_content_type', 'applicant_object_id')
    
    group = models.ForeignKey(TgGroup,null=True)
    request = models.TextField()
    status = models.PositiveIntegerField(default=PENDING)

    admin_comment = models.TextField(default='')
    date = models.DateField(auto_now_add=True)
    accepted_by = models.ForeignKey(User, null=True)


    def is_site_application(self) :
        """ Is this an application by someone who's not yet a site-member and needs an User / Profile object created"""

        if self.applicant.get_user() is None :
            return True
        return False

    def has_group_request(self) :
        """ Is this application requesting a group in addition to site membership?"""
        if self.group : 
            return True
        else :
            return False

    def accept(self,sponsor,site_root,**kwargs) :

        self.status = WAITING_USER_SIGNUP
        if kwargs.has_key('admin_comment') :
            self.admin_comment = kwargs['admin_comment']
            self.accepted_by = sponsor
        self.save()
        return self.applicant.accept_mail(sponsor, site_root, self.id)


    def get_approvers(self):
        return [u for u in get_all_members_group().get_admin_group().get_users()]

    
def create_notifications(sender, instance, **kwargs):
    if instance is None :
        return
    application = instance
    from notification import models as notification
    notification.send(instance.get_approvers(), "new_application", 
                      {'first_name':application.applicant.first_name,
                       'last_name':application.applicant.last_name,
                       'organisation':application.applicant.organisation,
                       'find_out':application.applicant.find_out,
                       'request':application.request
                       })
    print "sent a notification to %s" % instance.get_approvers()
    
    
if "notification" in settings.INSTALLED_APPS:
    post_save.connect(create_notifications,sender=Application)




