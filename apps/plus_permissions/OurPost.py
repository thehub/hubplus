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

 
