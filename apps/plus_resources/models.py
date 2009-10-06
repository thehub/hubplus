from django.db import models
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from apps.plus_permissions.models import GenericReference

from apps.plus_lib.models import extract

def get_resources_for(owner) :
    return Resource.objects.filter(in_agent=owner.get_ref())
    

def upload_to(instance, file_name) :
    owner = instance.in_agent.obj
    owner_class = ContentType.objects.get_for_model(owner)
    owner_id = owner.id
    return "member_resources/%s/%s/%s/%s" % (owner_class, owner_id, instance.id, file_name)

class Resource(models.Model):

    in_agent = models.ForeignKey(GenericReference, related_name="resources")

    title = models.CharField(max_length=100)
    description = models.TextField()
    
    author = models.CharField(max_length=100)
    license = models.CharField(max_length=50)

    resource = models.FileField(upload_to=upload_to)
    created_by = models.ForeignKey(User, related_name="created_resource", null=True) 

    # XXX 
    # for compatibility with code
    stub = models.BooleanField(default=True) # for compatibility with content creation
    name = models.CharField(max_length=100)


    def download_url(self) :
        return self.resource.url

   
def get_or_create(user, owner, **kwargs) :

    resources = Resource.objects.filter(in_agent=owner.get_ref(),name=kwargs['name'])
    if resources.count() < 1 :
        resource = Resource(in_agent=owner.get_ref(), title=kwargs['title'], description=kwargs['description'],
                        author=kwargs['author'], license=kwargs['license'])
        resource.save()
        if kwargs.has_key('resource') :
            resource.resource = kwargs['resource']
        resource.save()
    else :
        resource = resources[0]
        resource.in_agent = owner.get_ref()
        dummy = extract(kwargs,'in_agent')
        for k,v in kwargs.iteritems() :
            setattr(resource, k, v)
    resource.save()
    return resource
