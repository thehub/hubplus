from django.db import models

from django.contrib.auth.models import User, UserManager
from django.contrib.contenttypes.models import ContentType

from apps.plus_permissions.models import get_permission_system

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from apps.hubspace_compatibility.models import TgGroup

from apps.plus_permissions.permissionable import PermissionableMixin




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

class ApplicationManager(models.Manager) :
    # only show applications to those who have right permissions
    # if query is done with "permission_agent" as argument

    def filter(self,**kwargs) :
        if not kwargs.has_key('permission_agent') :
            return super(ApplicationManager,self).filter(**kwargs)
        else :
            agent = kwargs['permission_agent']
            del kwargs['permission_agent']
            ps = get_permission_system()
            return (a for a in super(ApplicationManager,self).filter(**kwargs) if ps.has_access(agent,a,ps.get_interface_id(Application,'Viewer')))


class Application(PermissionableMixin, models.Model) :
    applicant_content_type = models.ForeignKey(ContentType,related_name='applicant_type')
    applicant_object_id = models.PositiveIntegerField()
    applicant = generic.GenericForeignKey('applicant_content_type', 'applicant_object_id')
    

    group = models.ForeignKey(TgGroup,null=True)
    request = models.TextField()
    status = models.PositiveIntegerField(default=PENDING)

    admin_comment = models.TextField(default='')
    date = models.DateField(auto_now_add=True)

    objects = ApplicationManager()

def extract(d,key) :
    if d.has_key(key) :
        v = d[key]
        del d[key]
    else :
        v = None
    return v

def make_plus_application(**kwargs) :
    security_context = extract(kwargs,'security_context')
    pa = Application(**kwargs)
    pa.save()
    if security_context :
        pa.set_security_context(security_context)
    return pa

