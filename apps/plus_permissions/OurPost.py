
# Permissions for OurPost, an example 

from django.db import models

from models import Interface, Slider, SecurityTag, PermissionManager
from models import InterfaceReadProperty, InterfaceWriteProperty
from models import get_permission_system, default_admin_for, PermissionableMixin

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from permissionable import *

from apps.hubspace_compatibility.models import TgGroup

import ipdb

# This represents a typical model type from another django or pinax app

class OurPost(PermissionableMixin, models.Model) :
    title = models.CharField(max_length='20')
    body = models.CharField(max_length='20')

    def __str__(self) :
        return "OurPost %s,%s" % (self.title,self.body)


    def foo(self) :
        pass


# Here's the wrapping we have to put around it.

class OurPostViewer(Interface) : 
    @classmethod 
    def get_id(cls) :
        return 'OurPost.Viewer'
    
    title = InterfaceReadProperty('title')
    body = InterfaceReadProperty('body')

class OurPostEditor(Interface) : 
    @classmethod 
    def get_id(cls) :
        return 'OurPost.Editor'

    title = InterfaceWriteProperty('title')
    body = InterfaceWriteProperty('body')

    @classmethod
    def delete(self) :
        return True

class OurPostCommentor(Interface) : 
    @classmethod
    def get_id(cls) :
        return 'OurPost.Commentor'


class OurPostPermissionManager(PermissionManager) :
    def register_with_interface_factory(self,interface_factory) :
        self.interface_factory = interface_factory
        interface_factory.add_type(OurPost)
        interface_factory.add_interface(OurPost,'Viewer',OurPostViewer)
        interface_factory.add_interface(OurPost,'Editor',OurPostEditor)
        interface_factory.add_interface(OurPost,'Commentor',OurPostCommentor)



    def setup_defaults(self,resource, owner, creator) :
        options = self.make_slider_options(resource,owner,creator)
        self.save_defaults(resource,owner,creator)
        interfaces = self.get_interfaces()
        s = interfaces['Viewer'].make_slider_for(resource,options,owner,0,creator)
        s = interfaces['Editor'].make_slider_for(resource,options,owner,2,creator)
        s = interfaces['Commentor'].make_slider_for(resource,options,owner,1,creator)
 

