from django.db import models
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from apps.plus_permissions.models import GenericReference



def make_file_path(owner_class, owner_id, resource_id) :
    return "member_resources/%s/%s/%s" % (owner_class, owner_id, resource_id)

def get_resources_for(owner) :
    content_type = ContentType.objects.get_for_model(owner)
    return Resource.objects.filter(owner_type=content_type, owner_id=owner.id)
    
class Resource(models.Model):
    owner_type = models.ForeignKey(ContentType, related_name='resource_owner_type')
    owner_id = models.PositiveIntegerField()
    owner = generic.GenericForeignKey('owner_type','owner_id')

    title = models.CharField(max_length=100)
    description = models.TextField()
    
    uploader = models.ForeignKey(User)
    author = models.CharField(max_length=100)
    license = models.CharField(max_length=50)

    resource = models.FileField(upload_to='resources')


    # XXX not entirely sure we should be having these. smells wrong to add extra fields to data just 
    # for compatibility with code
    stub = models.BooleanField(default=True) # for compatibility with content creation
    in_agent = models.ForeignKey(GenericReference, related_name="uploaded_resources") # for compatibility with content creation
    name = models.CharField(max_length=100)


    def download_url(self) :
        owner_class= ContentType.objects.get_for_model(self.owner).model
        owner_id = self.owner.id

        return "%s/%s/%s" % (settings.MEDIA_URL, 
                             make_file_path(owner_class, owner_id, self.id),
                             self.resource.name)
   


