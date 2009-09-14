from django.db import models
from apps.plus_permissions.models import GenericReference
from django.contrib.auth.models import User

class WikiPage(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
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
