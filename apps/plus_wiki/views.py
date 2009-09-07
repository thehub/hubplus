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


@login_required
def create_wiki(request, template_name="plus_wiki/create_wiki.html"):

    return render_to_response(template_name, {
            }, context_instance=RequestContext(request))


