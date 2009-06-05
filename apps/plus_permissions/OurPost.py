# Permissions for OurPost, an example 

from django.db import models

from models import Interface, Slider, SliderOption, SecurityTag, PermissionManager, AgentNameWrap
from models import get_permission_system, default_admin_for

from apps.hubspace_compatibility.models import TgGroup

# This represents a typical model type from another django or pinax app

class OurPost(models.Model) :
    title = models.CharField(max_length='20')


# Here's the wrapping we have to put around it.

class OurPostViewer(Interface) : pass
class OurPostEditor(Interface) : pass
class OurPostCommentor(Interface) : pass


class OurPostViewerSlider(Slider) :
    def __init__(self,creator,owner) :
        self.options = [SliderOption(name,agent) for (name,agent) in [
                        ('root',get_permission_system().get_anon_group()),
                        ('all_members',get_permission_system().get_all_members_group()),
                        (AgentNameWrap(owner).name,owner),
                        (AgentNameWrap(creator).name,creator),
                        (AgentNameWrap(default_admin_for(owner)).name,default_admin_for(owner))
                        ]]
        self.set_current_option(0)

class OurPostPermissionManager(PermissionManager) :
    def register_with_interface_factory(self,interface_factory) :
        self.interface_factory = interface_factory
        interface_factory.add_type(OurPost)
        interface_factory.add_interface(OurPost,'Viewer',OurPostViewer)
        interface_factory.add_interface(OurPost,'Editor',OurPostEditor)
        interface_factory.add_interface(OurPost,'Commentor',OurPostCommentor)


    def make_viewer_slider(self,resource,interface_name,owner,creator) :
        options = [
            SliderOption('root',get_permission_system().get_anon_group()),
            SliderOption('all_members',get_permission_system().get_all_members_group()),
            SliderOption(AgentNameWrap(owner).name,owner),
            SliderOption(AgentNameWrap(creator).name,creator)
        ]
        default_admin = default_admin_for(owner)
        if not default_admin is None :
            options.append( SliderOption(AgentNameWrap(default_admin).name,default_admin) )
        
        for o in options :
            print o.name, o.agent
            
        s = Slider(
            tag_name='OurPostPermissionManager.Viewer slider',
            resource=resource,
            interface_id='OurPostPermissionManager.Viewer',
            default_agent=self.get_permission_system().get_anon_group(),
            options=options
        )

        s.set_current_option(0)
        return s



    def make_slider(self,resource,interface_name,owner,creator) :
        if interface_name == 'Viewer' :
            return self.make_viewer_slider(resource,interface_name,owner,creator)
        elif interface_name == 'Editor' :
            return Slider()
        elif interface_name == 'Commentor' : 
            return Slider()
        else :
            raise NoSliderException(OurPost,interface_name)
               
