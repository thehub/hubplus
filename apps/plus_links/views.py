from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import simplejson
from models import Service, Link
from forms import LinkForm
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from apps.plus_permissions.api import secure_resource
from django.template import RequestContext
from django.template.loader import get_template
from django.utils import simplejson
from django.contrib.contenttypes.models import ContentType

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
            link_html = get_template('plus_links/one_link.html').render(RequestContext(request, {'text':link.text, 'url':link.url, 'link_id':link.id, 'can_delete':hasattr(link, 'delete') and True or False}))
            data = simplejson.dumps({'new_link':link_html})
            return HttpResponse(data, mimetype='application/json')
        else :
            list_and_form_err = get_template('plus_links/errors.html').render(RequestContext(request, {'form_data':form.data, 'errors':form.errors, 'target_id':target.id, 'target_class':ContentType.objects.get_for_model(target.get_inner()).id}))
            data = simplejson.dumps({'list_and_form':list_and_form_err})
            return HttpResponse(data, mimetype='application/json')


            
@login_required
@secure_resource(Link)
def remove_link(request, link) :
    try:
        link.delete()
        data = simplejson.dumps({'deleted':"true"})
    except Exception, e :
        data = simplejson.dumps({'error':'%s'%e})

    return HttpResponse(data, mimetype='application/json')
