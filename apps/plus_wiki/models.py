from django.db import models
from apps.plus_permissions.models import GenericReference
from django.contrib.auth.models import User


class WikiPage(models.Model):
    class Meta:
        unique_together = (("name", "in_agent"),)
    name = models.CharField(max_length=100)

    @classmethod
    def check_name(self, name, in_agent, obj=None):
        try:
            page = WikiPage.objects.get(name=name, in_agent=in_agent)
            if obj and obj.id == page.id:
                pass
            else:
                raise ValueError("Can't change name to %s, a WikiPage of that name already exists in this group" % name)
        except WikiPage.DoesNotExist:
            pass

    def set_name(self, name):
        self.check_name(name, self.in_agent, obj=self)
        self.name = name

    title = models.CharField(max_length=100)
    def display_name(self):
        return self.title

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


    def delete(self) :
        ref = self.get_ref()
        ref.delete()
        super(WikiPage,self).delete()



import reversion
try:
    reversion.register(WikiPage)
except reversion.revisions.RegistrationError:
    pass

class VersionDelta(models.Model):
    revision = models.ForeignKey("reversion.Revision") 
    delta = models.TextField(blank=True)  # delta to the previous version for the purposes of feeds

#redirects model
