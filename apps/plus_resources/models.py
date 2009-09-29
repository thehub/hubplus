from django.db import models
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from apps.plus_permissions.models import GenericReference


def make_file_path(owner_class, owner_id, resource_id) :
    return "member_resources/%s/%s/%s" % (owner_class, owner_id, resource_id)

def get_resources_for(owner) :
    return Resource.objects.filter(in_agent=owner.get_ref())
    
class Resource(models.Model):

    in_agent = models.ForeignKey(GenericReference, related_name="resources")

    title = models.CharField(max_length=100)
    description = models.TextField()
    
    uploader = models.ForeignKey(User)
    author = models.CharField(max_length=100)
    license = models.CharField(max_length=50)

    resource = models.FileField(upload_to='resources')
    created_by = models.ForeignKey(User, related_name="created_resource", null=True) 

    # XXX 
    # for compatibility with code
    stub = models.BooleanField(default=True) # for compatibility with content creation
    name = models.CharField(max_length=100)


    def download_url(self) :
        owner_class= ContentType.objects.get_for_model(self.in_agent.obj).model
        owner_id = self.in_agent.obj.id

        return "%s/%s/%s" % (settings.MEDIA_URL, 
                             make_file_path(owner_class, owner_id, self.id),
                             self.resource.name)
   


