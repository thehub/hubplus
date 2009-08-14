from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User

class MissingSecurityContextException(Exception): 
    def __init__(self, cls, security_context) :
        self.cls = cls
        self.security_context = security_context
        self.msg = 'Missing %s when creating a %s' % (context,cls)


class MissingSecurityContextException(Exception): 
    def __init__(self, cls, security_context) :
        self.cls = cls
        self.security_context = security_context
        self.msg = 'Missing %s when creating a %s' % (context,cls)


class PermissionSystemContextManager(models.Manager) :

    def get_or_create(self,target) :
        target_type = ContentType.objects.get_for_model(target)
        if Context.objects.filter(target_content_type=target_type,target_object_id=target.id).count() == 0:
            cn = Context(target=target)
            cn.save()
            return cn
        else :
            cn = Context.objects.get(target_content_type=target_type,target_object_id=target.id)
            return cn



class Context(models.Model):
    """ Maps any content_type target to a security_context and context """
    target_content_type = models.ForeignKey(ContentType,related_name='context_target', null=True)
    target_object_id = models.PositiveIntegerField(null=True)
    target = generic.GenericForeignKey('target_content_type', 'target_object_id')

    security_context_content_type = models.ForeignKey(ContentType,related_name='security_context', null=True)
    security_context_object_id = models.PositiveIntegerField(null=True)
    security_context = generic.GenericForeignKey('security_context_content_type', 'security_context_object_id')

    context_content_type = models.ForeignKey(ContentType,related_name='context', null=True)
    context_object_id = models.PositiveIntegerField(null=True)
    context = generic.GenericForeignKey('context_content_type', 'context_object_id')

    objects = PermissionSystemContextManager()

    def __str__(self) :
        return """target:%s, security context:%s, context:%s""" % (self.target,self.security_context,self.context)


