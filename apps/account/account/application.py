from django.db import models
from django.conf import settings
from apps.plus_groups.models import TgGroup

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class Application(models.Model) :
    applicant_content_type = models.ForeignKey(ContentType,related_name='applicant_type')
    applicant_object_id = models.PositiveIntegerField()
    applicant = generic.GenericForeignKey('agent_content_type', 'agent_object_id')

    group = models.ForeignKey(TgGroup)
    request = models.TextField()
    status = models.PositiveIntegerField(default=0)





