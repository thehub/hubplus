from django.db import models
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from apps.plus_permissions.models import GenericReference
from datetime import datetime
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

class NameConflictException(Exception) :
    pass

class Resource(models.Model):

    in_agent = models.ForeignKey(GenericReference, related_name="resources")

    title = models.CharField(max_length=100)
    def display_name(self):
        return self.title
    
    @classmethod
    def check_name(self, name, in_agent, obj=None):
        try:
            res = Resource.objects.get(name=name, in_agent=in_agent)
            if obj and obj.id==res.id:
                pass
            else:
                raise ValueError("Can't change name to %s, a Resource of that name already exists in this group" % name)
        except Resource.DoesNotExist:
            pass

    def set_name(self, name):
        self.check_name(name, self.in_agent, obj=self)
        self.name = name

    description = models.TextField(default='')

    author = models.CharField(max_length=100)
    license = models.CharField(max_length=50)

    resource = models.FileField(upload_to=upload_to)
    created_by = models.ForeignKey(User, related_name="created_resource", null=True) 

    stub = models.BooleanField(default=True) # for compatibility with content creation
    name = models.CharField(max_length=100)


    def move_to_new_group(self, group) :
        try : 
            Resource.check_name(self.name, group.get_ref(), self)
        except ValueError, e:
            raise NameConflictException(_("Group %(group_name)s already has an upload called %(upload_name)")%{'group_name':group.group_name,'upload_name':name})
        # change in_agent
        self.in_agent = group.get_ref()
        # change security_context
        self.acquires_from(group)
        self.save()
        

    def download_url(self) :
        if self.resource :
            return self.resource.url
        else :
            return ''

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

    def rename_file(self, new_file_name,sep='/') :
        # NB: only changes the actual file name
        file = self.resource.file
        file_path = file.name.split(sep)
        old_name = file_path[-1]
        print old_name, ' to ', new_file_name
        
        file_path[-1]=new_file_name
        new_path = sep.join(file_path)

        try :
            f = File(open(file.name,'rb'))
            self.resource = f
            self.resource.name = new_path
            self.save()
            f.close()
            
        except Exception, e :
            print e

    def comment(self) :
        pass
        # dummy, for testing

    def delete(self) :
        ref = self.get_ref()
        ref.delete()
        super(Resource,self).delete()

    def save(self):
        super(Resource, self).save()
        ref = self.get_ref()
        ref.modified = datetime.now()
        ref.display_name = self.get_display_name()
        ref.save()


def update_attributes(resource_obj, user, **kwargs) :

    resource_obj.title = kwargs['title']
    resource_obj.name = kwargs['name']
    resource_obj.description= kwargs['description']
    resource_obj.author = kwargs['author']
    resource_obj.license = kwargs['license']

    resource_obj.save()

    if kwargs.has_key('resource') and kwargs['resource'] :
        try :
            resource_obj = resource_obj.get_inner()
        except :
            pass
        resource_obj.resource = kwargs['resource']
        resource_obj.created_by = user
        resource_obj.save()

    return resource_obj

