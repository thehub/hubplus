# Permissions for OurPost, an example 

from django.db import models

from models import Interface, Slider, SliderOption, SecurityTag, PermissionManager
from models import InterfaceReadProperty, InterfaceWriteProperty
from models import get_permission_system, default_admin_for

from apps.hubspace_compatibility.models import TgGroup

# This represents a typical model type from another django or pinax app

class OurPost(models.Model) :
    title = models.CharField(max_length='20')
    body = models.CharField(max_length='20')

    def __str__(self) :
        return "OurPost" #%s,%s" % (self.title,self.body)

# Here's the wrapping we have to put around it.

class OurPostViewer(Interface) : 
    title = InterfaceReadProperty('title')
    body = InterfaceReadProperty('body')

class OurPostEditor(Interface) : 
    title = InterfaceWriteProperty('title')
    body = InterfaceWriteProperty('body')
    @classmethod
    def delete(self) :
        return True

class OurPostCommentor(Interface) : 
    pass


class OurPostPermissionManager(PermissionManager) :
    def register_with_interface_factory(self,interface_factory) :
        self.interface_factory = interface_factory
        interface_factory.add_type(OurPost)
        interface_factory.add_interface(OurPost,'Viewer',OurPostViewer)
        interface_factory.add_interface(OurPost,'Editor',OurPostEditor)
        interface_factory.add_interface(OurPost,'Commentor',OurPostCommentor)

    def make_slider_options(self,resource,interface_name,owner,creator) :
        options = [
            SliderOption('root',get_permission_system().get_anon_group()),
            SliderOption('all_members',get_permission_system().get_all_members_group()),
            SliderOption(owner.display_name,owner),
            SliderOption(creator.display_name,creator)
        ]

        default_admin = default_admin_for(owner)

        if not default_admin is None :
            options.append( SliderOption(default_admin.display_name,default_admin) )

        return options

    def make_viewer_slider(self,resource,interface_name,owner,creator) :
        options = self.make_slider_options(resource,interface_name,owner,creator)
        s = Slider(
            tag_name='OurPostPermissionManager.Viewer slider',
            resource=resource,
            interface_id='OurPost.Viewer',
            default_agent=self.get_permission_system().get_anon_group(),
            options=options
        )
        s.set_current_option(0)
        return s

    def make_editor_slider(self,resource,interface_name,owner,creator) :
        options = self.make_slider_options(resource,interface_name,owner,creator)
        s = Slider(
            tag_name='OurPostPermissionManager.Editor slider',
            resource=resource,
            interface_id='OurPost.Editor',
            default_agent=self.get_permission_system().get_anon_group(),
            options=options
        )
        s.set_current_option(3)
        return s


    def make_commentor_slider(self,resource,interface_name,owner,creator) :
        options = self.make_slider_options(resource,interface_name,owner,creator)
        s = Slider(
            tag_name='OurPostPermissionManager.Commentor slider',
            resource=resource,
            interface_id='OurPost.Commentor',
            default_agent=self.get_permission_system().get_anon_group(),
            options=options
        )
        s.set_current_option(0)
        return s


    def make_slider(self,resource,interface_name,owner,creator) :
        if interface_name == 'Viewer' :
            return self.make_viewer_slider(resource,interface_name,owner,creator)
        elif interface_name == 'Editor' :
            return self.make_editor_slider(resource,interface_name,owner,creator)
        elif interface_name == 'Commentor' : 
            return self.make_commentor_slider(resource,interface_name,owner,creator)
        else :
            raise NoSliderException(OurPost,interface_name)
               
    def setup_defaults(self,resource, owner, creator) :
        s = self.make_slider(resource,'Viewer',owner,creator)
        s.set_current_option(s.current_idx)
        s = self.make_slider(resource,'Editor',owner,creator)
        s.set_current_option(s.current_idx)
        s = self.make_slider(resource,'Commentor',owner,creator)
        s.set_current_option(s.current_idx)

