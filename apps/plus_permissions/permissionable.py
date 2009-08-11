from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User

class PermissionSystemContextManager(models.Manager) :

    def get_or_create(self,target) :
        target_type = ContentType.objects.get_for_model(target)
        if Context.objects.filter(target_content_type=target_type,target_object_id=target.id).count() == 0 :
            cn = Context(target=target)
            cn.save()
            return cn
        else :
            cn = Context.objects.get(target_content_type=target_type,target_object_id=target.id)
            return cn

    def set_security_context(self,target,context) :
        cn = self.get_or_create(target)
        cn.security_context = context
        cn.save()
    
    def set_context(self,target,context):
        cn = self.get_or_create(target)
        cn.context = context
        cn.save()

    def get_security_context(self,target) :
        return self.get_or_create(target).security_context

    def get_context(self,target) :
        return self.get_or_create(target).context


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

class MissingContextException(Exception): 
    def __init__(self,cls,context) :
        self.cls = cls
        self.context = context
        self.msg = 'Missing %s when creating a %s' % (context,cls)

class PermissionableMixin :
    """ Use to add context handling to other classes """
    def set_security_context(self,context) :
        return Context.objects.set_security_context(self,context)

    def get_security_context(self) :
        return Context.objects.get_security_context(self)

    def set_context(self,context) :
        return Context.objects.set_context(self,context)

    def get_context(self) :
        return Context.objects.get_context(self)

