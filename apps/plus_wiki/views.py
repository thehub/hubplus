from django.conf import settings

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User

from django.template import RequestContext
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import models

from django.template import RequestContext
from apps.plus_groups.models import TgGroup
from apps.plus_permissions.api import secure_resource

@login_required
@secure_resource(TgGroup)
def create_wiki(request, group, template_name="plus_wiki/create_wiki.html"):
    return render_to_response(template_name, {
            }, context_instance=RequestContext(request))


@login_required
@secure_resource(TgGroup)
def edit_wiki(request, group, page_name, template_name="plus_wiki/create_wiki.html"):
    return render_to_response(template_name, {
            }, context_instance=RequestContext(request))

    
