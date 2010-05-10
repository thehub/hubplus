from django.db import models
from django.conf import settings
from datetime import datetime
 
class Explorable(models.Model) :
    class Meta:
        abstract = True

    def get_url(self) :
        return "URL TO %s, %s" % (self.__class__.__name__, self.id)

    def get_display_name(self) :
        return self.get_ref().display_name

    def get_description(self) :
        return "DESCRIPTION OF %s, %s" % (self.__class__.__name__, self.id)

    def get_author_name(self) :
        return self.get_ref().creator.get_ref().display_name

    def get_author_copyright(self) :
        return "AUTHOR COPYRIGHT of %s, %s" % (self.__class__.__name__, self.id)

    def get_created_date(self) :
        return self.get_ref().modified

    def get_feed_extras(self) :
        return {}
