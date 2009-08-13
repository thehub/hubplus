from django.db import models
from django.conf import settings
from apps.hubspace_compatibility.models import TgGroup

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

PENDING = 0

class Application(models.Model) :
    applicant_content_type = models.ForeignKey(ContentType,related_name='applicant_type')
    applicant_object_id = models.PositiveIntegerField()
    applicant = generic.GenericForeignKey('applicant_content_type', 'applicant_object_id')

    group = models.ForeignKey(TgGroup,null=True)
    request = models.TextField()
    status = models.PositiveIntegerField(default=PENDING)





