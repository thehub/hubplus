from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.db import transaction
from django.utils import simplejson


@login_required
def update_main_permission_sliders(request,username) :
    ps = get_permission_system()
    pm = ps.get_permission_manager(Profile)
    p = request.user.get_profile()

    form = request.form()
    json = pm.main_json_slider_group(p)
    print json
    return HttpResponse(json, mimetype='text/plain')
