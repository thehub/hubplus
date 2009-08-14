from django.db import models

from django.contrib.auth.models import User, UserManager
from django.contrib.contenttypes.models import ContentType

from apps.plus_permissions.models import get_permission_system

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from apps.hubspace_compatibility.models import TgGroup

from apps.plus_permissions.permissionable import PermissionableMixin
from django.core.mail import send_mail

from django.conf import settings

class PlusContact(models.Model):
    """Use this for the sign-up / invited sign-up process, provisional users"""
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    organisation = models.CharField(max_length=255)
    email_address = models.CharField(max_length=255,unique=True)
    location = models.CharField(max_length=100)
    apply_msg = models.TextField()
    find_out = models.TextField()
    invited_by = models.ForeignKey(User,null=True)


    def get_user(self) :
        if len( User.objects.filter(email_address=self.email_address) ) < 1 : 
            return None
        return User.objects.get(email_address=self.email_address)

    def become_member(self, username, invited_by=None, accepted_by=None):
        """Either a user accepts an invitation or their application is accepted.
        XXX If application is accepted trigger an email with confirmation page to set password
        XXX if invitation is accepted by user then they go straight to set password page
        """
        u = User.objects.create_user(username, self.email_address)
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
        ps = get_permission_system()
        ps.get_site_members().add_member(u)
        self.delete()
        return u



PENDING = 0
WAITING_USER_SIGNUP = 1

class ApplicationManager(models.Manager) :
    # only show applications to those who have right permissions
    # if query is done with "permission_agent" as argument

    def filter(self,**kwargs) : 
        if not kwargs.has_key('permission_agent') :
            return super(ApplicationManager,self).filter(**kwargs)
        else :
            from apps.plus_permissions.models import NullInterface
            agent = kwargs['permission_agent']
            del kwargs['permission_agent']
            ps = get_permission_system()
            def wrap(a) :
                n = NullInterface(a)
                n.load_interfaces_for(agent)
                
            return (wrap(a) 
                    for a in super(ApplicationManager,self).filter(**kwargs) 
                    if ps.has_access(agent,a,ps.get_interface_id("Application",'Viewer')))


    def get(self,**kwargs) :
        if not kwargs.has_key('permission_agent') :
            return super(ApplicationManager,self).get(**kwargs)
        else :
            from apps.plus_permissions.models import NullInterface
            agent = kwargs['permission_agent']
            del kwargs['permission_agent']
            ps = get_permission_system()
            
            a = super(ApplicationManager,self).get(**kwargs)
            
            n = NullInterface(a)
            n.load_interfaces_for(agent)
            return n

class Application(PermissionableMixin, models.Model) :
    applicant_content_type = models.ForeignKey(ContentType,related_name='applicant_type')
    applicant_object_id = models.PositiveIntegerField()
    applicant = generic.GenericForeignKey('applicant_content_type', 'applicant_object_id')
    
    group = models.ForeignKey(TgGroup,null=True)
    request = models.TextField()
    status = models.PositiveIntegerField(default=PENDING)

    admin_comment = models.TextField(default='')
    date = models.DateField(auto_now_add=True)
    accepted_by = models.ForeignKey(User, null=True) 

    objects = ApplicationManager()

    def generate_accept_url(self, accepted_by) :
        url = '/contacts/signup/%s/%s' % (self.applicant.id,accepted_by.id)
        return url


    def is_site_application(self) :
        """ Is this an application by someone who's not yet a site-member and needs an User / Profile object created"""

        if self.applicant.get_user() is None :
            return True
        return False

    def requests_group(self) :
        """ Is this application requesting a group in addition to site membership?"""
        if self.group : 
            return True
        else :
            return False

    def accept(self,sponsor,**kwargs) :
        self.status = WAITING_USER_SIGNUP
        if kwargs.has_key('admin_comment') :
            self.admin_comment = kwargs['admin_comment']
            self.accepted_by = sponsor
        self.save()

        url = self.generate_accept_url(sponsor)

        message = """
Dear %s %s,
We are delighted to confirm you have been accepted as a member of Hub+

Please visit the following link to confirm your account : %s
""" % (self.applicant.first_name, self.applicant.last_name, url)

        email_address = self.applicant.email_address

        print settings.EMAIL_HOST, settings.EMAIL_PORT
        send_mail('Confirmation of account on Hub+', message, settings.CONTACT_EMAIL,
                  [self.applicant.email_address], fail_silently=False)
        
        print "Done email"
        return message, url


def extract(d,key) :
    if d.has_key(key) :
        v = d[key]
        del d[key]
    else :
        v = None
    return v

def make_application(**kwargs) :
    security_context = extract(kwargs,'security_context')
    pa = Application(**kwargs)
    pa.save()
    # setup security context
    if security_context :
        pa.set_security_context(security_context)
    elif pa.group :
        pa.set_security_context(pa.group)
    else :
        pa.set_security_context(get_permission_system().get_site_members())

    # and we give view permission to any site-member
    ps = get_permission_system()
    tag = ps.create_security_tag(pa.get_security_context(),ps.get_interface_id(Application,'Viewer'),[pa.get_security_context()])
    tag2 = ps.create_security_tag(pa.get_security_context(),ps.get_interface_id(Application,'Accepter'),[pa.get_security_context()])

    pa.save()    
    return pa

