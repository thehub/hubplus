# Permissions for OurPost, an example 

from django.db import models
from models import Interface, Slider, SliderOption, SecurityTag, PermissionManager

from apps.hubspace_compatibility.models import TgGroup

# This represents a typical model type from another django or pinax app

class OurPost(models.Model) :
    title = models.CharField(max_length='20')


# Here's the wrapping we have to put around it.

class OurPostViewer(Interface) : pass
class OurPostEditor(Interface) : pass
class OurPostCommentor(Interface) : pass


class OurPostSlider(Slider) :
    def set_current_option(self,idx) :
        Slider.set_current_option(self,idx)
        


class OurPostViewerSlider(OurPostSlider) :
    def __init__(self) :
        self.options = [SliderOption(x) for x in 'anon','members','group members', 'me']
        self.set_current_option(0)

class OurPostEditorSlider(OurPostSlider) :
    def __init__(self) :
        self.options = []
        self.set_current_option(3)

class OurPostCommentorSlider(OurPostSlider) :
    def __init__(self) :
        self.options = []
        self.set_current_option(2)


class OurPostPermissionDefaults :
    def __init__(self, agent, resource) :
        self.sliders = {
            'Viewer' : OurPostViewerSlider(),
            'Editor' : OurPostEditorSlider(),
            'Commentor' : OurPostCommentorSlider()
            }

    def has_extras(self) :
        return False

    def is_changed(self) :
        return False

    def get_sliders(self) :
        return self.sliders

    def get_slider(self,name) :
        return self.sliders[name]



class OurPostPermissionManager(PermissionManager) :
    def register_with_interface_factory(self,interface_factory) :
        self.interface_factory = interface_factory
        interface_factory.add_type(OurPost)
        interface_factory.add_interface(OurPost,'Viewer',OurPostViewer)
        interface_factory.add_interface(OurPost,'Editor',OurPostEditor)
        interface_factory.add_interface(OurPost,'Commentor',OurPostCommentor)

 
    def setup_defaults(self,an_agent,resource) :
        pd = OurPostPermissionDefaults(an_agent,resource)
        everyone = self.get_permission_system().get_anon_group()
        tag =  SecurityTag(name='default_viewer',agent=everyone,resource=resource,interface=self.interface_factory.get_id(OurPost,'Viewer'))
        tag.save()

        tag2 = SecurityTag(name='default_editor',agent=an_agent,resource=resource,interface=self.interface_factory.get_id(OurPost,'Editor'))
        tag2.save()

        tag3 = SecurityTag(name='default_commentor',agent=an_agent,resource=resource,interface=self.interface_factory.get_id(OurPost,'Commentor'))
        tag3.save()

        return pd
