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

class Contributions(models.Model):
    wikipage = models.ForeignKey(WikiPage, related_name='contributions')
    user = models.ForeignKey(User, related_name='contributions')
    what_changed = models.TextField(blank=True)
    # time_saved = ForeignKey
    # delta

#redirects 
