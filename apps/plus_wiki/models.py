from django.db import models
from apps.plus_permissions.models import GenericReference
from django.contrib.auth.models import User


from apps.plus_groups.resources_common import resource_common

class WikiPage(models.Model):
    class Meta:
        unique_together = (("name", "in_agent"),)
    name = models.CharField(max_length=100)

    def set_name(self, name):
        self.check_name(name, self.in_agent, obj=self)
        self.name = name

    title = models.CharField(max_length=100)
    def display_name(self):
        return self.title

    stub = models.BooleanField(default=True)
    copyright_holder = models.CharField(max_length=100, default='',null=True) 
    license = models.CharField(max_length=100)
    content = models.TextField(blank=True)  # html field
    links_to = models.ManyToManyField(GenericReference, related_name="back_links")
    in_agent = models.ForeignKey(GenericReference, related_name="wiki_pages")
    created_by = models.ForeignKey(User, related_name="created_wiki_pages", null=True) #stubs shouldn't be created by anyone or owned by anyone (imo) - t.s.
    creation_time = models.DateTimeField(auto_now_add=True)

    def comment(self) :
        """ XXX will refactor creating a comment on the wiki into this function, at the moment, 
        at the moment, used for permission testing"""
        pass

WikiPage = resource_common(WikiPage)

import reversion
try:
    reversion.register(WikiPage)
except reversion.revisions.RegistrationError:
    pass

class VersionDelta(models.Model):
    revision = models.ForeignKey("reversion.Revision") 
    delta = models.TextField(blank=True)  # delta to the previous version for the purposes of feeds

#redirects model
