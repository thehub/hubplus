from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import simplejson
from models import *
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound

# this collection must be kept up-to-date for each type of model which 
# CHANGE THIS
from apps.profiles.models import Profile
from apps.hubspace_compatibility.models import TgGroup

from django.contrib.contenttypes.models import ContentType

def tag_permission_test(fn) :
    """ Decorator for permissions for adding and removing tags. """
    def our_fn(request,*args,**kwargs) :
        ps = get_permission_system()
        target_class = request.POST['target_class']
        target_id = request.POST['target_id']

        try :
            cls = ContentType.objects.get(model=target_class)
            tagged_resource = cls.get_object_for_this_type(pk=target_id)
        except Exception, e :
            return HttpResponseNotFound("error evaling target_class %s : $%s$" % (target_class,e))
        
        if not ps.has_access(request.user,tagged_resource,ps.get_interface_id(cls,'Editor')) :
            return HttpResponse("You don't have permission to tag %s, you are %s" % (tagged_resource,request.user),status=401)
        else :
            return fn(request, tagged_resource, *args, **kwargs)
    return our_fn




@login_required
@tag_permission_test
@transaction.commit_on_success
def add_tag(request, tagged_resource):
    """ This is actually a way to add typed keywords (e.g. skills, interests, needs) as well as 'free tags'"""
    tag_type = request.POST['tag_type']
    tag_value = request.POST['tag_value']
    tagger = request.user
    tag, added = tag_add(tagged_resource, tag_type, tag_value, tagger)
    data = simplejson.dumps({'keyword':tag.keyword, 'tag_type':tag.tag_type, 'tagged':'yourself', 'added':added})
    return HttpResponse(data, mimetype='application/json')


@login_required
@transaction.commit_on_success
def autocomplete_tag(request, tag_type):
    q = request.GET['q']
    limit = request.GET['limit']
    options = tag_autocomplete(tag_type, q, limit)
    options = '\n'.join(options)
    return HttpResponse(options)

@login_required
@tag_permission_test
@transaction.commit_on_success
def delete_tag(request, tagged_resource):
    tag_type = request.POST['tag_type']
    tag_value = request.POST['tag_value']
    tagger = request.user
    tag, deleted = tag_delete(tagged_resource, tag_type, tag_value, tagger)
    data = simplejson.dumps({'deleted':deleted})
    return HttpResponse(data, mimetype='application/json')


def plot_tag(tag, depth=0):
    if depth:
        children = [plot_resource(resource, depth=depth-1) for resource in get_tagged_resources(tag.tag_type, tag.keyword)]
    else:
        children = []

    return {"id": 'tag' + "-" +str(tag.id),  
           "name": tag.keyword,  
           "data": {  
            'relation': "<h4>tag: %s </h4> " %(tag.keyword)  
            },  
           "children": children
           }

def plot_resource(resource, depth=0):
    if depth:
        children = [plot_tag(tag, depth=depth-1) for tag in get_tags(tagged = resource, tagger = resource.user, tag_type = 'skill')]
    else:
        children = []
    return {  
        "id": resource.__class__.__name__ + "-" +str(resource.id),  
        "name": resource.name,  
        "children": children,
        "data": {'relation':"<h4>%s</h4>" %(resource.name)}
     }


@login_required
def map_tags(request, tagged_resource):
    json = plot_resource(tagged_resource, depth=2)
    json = simplejson.dumps(json)
    return HttpResponse(json, mimetype='application/json')
