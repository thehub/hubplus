from django.db import models
from apps.plus_permissions.models import GenericReference
from django.contrib.auth.models import User
from django.conf import settings


from apps.plus_groups.resources_common import ResourceCommonModel
from django.utils.html import strip_tags

class WikiPage(ResourceCommonModel):

    copyright_holder = models.CharField(max_length=100, default='',null=True) 
    license = models.CharField(max_length=100)
    content = models.TextField(blank=True)  # html field
    links_to = models.ManyToManyField(GenericReference, related_name="back_links")

    creation_time = models.DateTimeField(auto_now_add=True)

    def comment(self) :
        """ XXX will refactor creating a comment on the wiki into this function, at the moment, 
        at the moment, used for permission testing"""
        pass

    def get_description(self) :
        return strip_tags(self.content)


import reversion
try:
    reversion.register(WikiPage)
except reversion.revisions.RegistrationError:
    pass

class VersionDelta(models.Model):
    revision = models.ForeignKey("reversion.Revision") 
    delta = models.TextField(blank=True)  # delta to the previous version for the purposes of feeds

#redirects model
