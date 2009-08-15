from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User

class MissingSecurityContextException(Exception): 
    def __init__(self, cls, security_context) :
        self.cls = cls
        self.security_context = security_context
        self.msg = 'Missing %s when creating a %s' % (context,cls)


class MissingSecurityContextException(Exception): 
    def __init__(self, cls, security_context) :
        self.cls = cls
        self.security_context = security_context
        self.msg = 'Missing %s when creating a %s' % (context,cls)


def security_patch(content_type):
    
