from django.db import models
from apps.plus_permissions.models import GenericReference
from django.contrib.auth.models import User
from apps.plus_groups.models import name_from_title

class WikiPage(models.Model):
    class Meta:
        unique_together = (("name", "in_agent"),)
    name = models.CharField(max_length=100)
    def name_from_title(self):
        #if name changes (and this is not a stub) we should set up a permanent redirect from here
        self.name = name_from_title(self.title)
        return self.name

    title = models.CharField(max_length=100)
    stub = models.BooleanField(default=True)
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

import reversion
try:
    reversion.register(WikiPage)
except reversion.revisions.RegistrationError:
    pass

class VersionDelta(models.Model):
    revision = models.ForeignKey("reversion.Revision") 
    delta = models.TextField(blank=True)  # delta to the previous version for the purposes of feeds

#redirects model
