from django.db import models
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from apps.plus_permissions.models import GenericReference

from apps.plus_lib.models import extract
from django.core.files.base import File

import os

def get_resources_for(owner) :
    return Resource.objects.filter(in_agent=owner.get_ref())
    
def get_permissioned_resources_for(user, owner) :
    return Resource.objects.plus_filter(user, in_agent=owner.get_ref(), required_interfaces=['Viewer'])

def upload_to(instance, file_name) :
    if '/' in file_name :
        file_name = file_name.split('/')[-1]
    owner = instance.in_agent.obj
    owner_class = ContentType.objects.get_for_model(owner)
    owner_id = owner.id
    return "member_res/%s/%s/%s/%s" % (owner_class, owner_id, instance.id, file_name)

class Resource(models.Model):

    in_agent = models.ForeignKey(GenericReference, related_name="resources")

    title = models.CharField(max_length=100)
    def display_name(self):
        return self.title

    description = models.TextField(default='')

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

    def display_name(self) :
        return self.title

    def content(self) :
        return self.description
#        return """%s
#%s,
#%s,
#%s""" % (self.title, self.description, self.author, self.created_by.get_display_name())
        


    def get_file_name(self) :
        if '/' in self.resource.file.name : 
            return self.resource.file.name.split('/')[-1]
        return self.resource.file.name

    def get_extension(self) :
        f_name = self.get_file_name()
        if not ('.' in f_name) :
            return '' # no extension
        else :
            return f_name.split('.')[-1]

    def change_extension(self, new_ext) :
        old_file_name = self.get_file_name()
        if not ('.' in old_file_name) : 
            return # no extension to change
        parts = old_file_name.split('.')
        parts[-1] = new_ext
        new_file_name = '.'.join(parts)
        self.rename_file(new_file_name)

    def rename_file(self, new_file_name) :
        # NB: only changes the actual file name
        file = self.resource.file
        file_path = file.name.split('/')
        old_name = file_path[-1]
        print old_name, ' to ', new_file_name
        
        file_path[-1]=new_file_name
        new_path = '/'.join(file_path)
        print "old ",file.name
        print "new ",new_path

        try :
            f = File(open(file.name,'rb'))
            self.resource = f
            self.resource.name = new_path
            self.save()
            f.close()
            
        except Exception, e :
            print e

def get_or_create(user, owner, **kwargs) :
    resources = Resource.objects.filter(in_agent=owner.get_ref(),name=kwargs['name'])

    if resources.count() < 1 :
        resource = owner.create_Resource(user, in_agent=owner.get_ref(), 
                                         title=kwargs['title'], description=kwargs['description'],
                                         author=kwargs['author'], license=kwargs['license'],
                                         created_by=user, name=kwargs['name'])
        resource.save()
        if kwargs.has_key('resource') :
            resource.get_inner().resource = kwargs['resource']  
        resource.save()
    else :
        resource = resources[0]
        try : 
            resource = resource.get_inner()
        except :
            pass
        resource.in_agent = owner.get_ref()
        resource.created_by = user
        dummy = extract(kwargs,'in_agent')
        dummy = extract(kwargs,'created_by')
        for k,v in kwargs.iteritems() :
            setattr(resource, k, v)

    resource.save()
    return resource
