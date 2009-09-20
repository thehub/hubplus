from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import simplejson
from models import Service, Link
from forms import LinkForm
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from apps.plus_permissions.api import secure_resource



@login_required
@secure_resource(obj_schema={'target':'any'})
def add_link(request, target):
    if request.POST :
        form = LinkForm(request.POST)
        if form.is_valid() :
            link = target.create_Link(request.user, target=target, 
                                      text = form.cleaned_data['text'],
                                      url = form.cleaned_data['url'],
                                      service=form.cleaned_data['service'])

            return render_to_response('plus_links/one_link.html',{'text':link.text, 'url':link.url})
        else :
            import ipdb
            ipdb.set_trace()
            return render_to_response('plus_links/error.html',{'errors':form.errors})

            
