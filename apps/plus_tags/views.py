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
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from apps.plus_permissions.api import secure_resource


@login_required
@secure_resource(obj_schema={'tagged':'any', 'tagged_for':[User, TgGroup]})
def add_tag(request, tagged, tagged_for=None):
    """ This is actually a way to add typed keywords (e.g. skills, interests, needs) as well as 'free tags'"""
    tagged_by = request.user
    if not tagged_for:
        tagged_for = tagged_by
    tag_type = request.POST['tag_type']
    tag_value = request.POST['tag_value']
    tag, added = tag_add(tagged, tag_type, tag_value, tagged_by)
    data = simplejson.dumps({'keyword':tag.keyword, 'tag_type':tag.tag_type, 'tagged':'yourself', 'added':added}) #why yourself?
    return HttpResponse(data, mimetype='application/json')


@login_required
@secure_resource(obj_schema={'tagged':'any', 'tagged_for':[User, TgGroup]})
def autocomplete_tag(request, tag_type, tagged=None, tagged_for=None):
    """
      - autocomplete should look for a partial match in the following in order until it finds 10 results:
      1. the users tags, 
      2. the tags of the resource's agent 
      3. all the user's enclosures, 
      4. all tags in the system ++ filter by the type of tags

      for now its very basic and completes on the tag_type and the partial value, globally
      """
    tagged_by = request.user
    if not tagged_for:
        tagged_for = tagged_by
    q = request.GET['q']
    limit = request.GET['limit']
    options = tag_autocomplete(tagged_for, tagged, tag_type, q, limit)
    options = '\n'.join(options)
    return HttpResponse(options)

@login_required
@secure_resource(obj_schema={'tagged':'any', 'tagged_for':[User, TgGroup]})
def delete_tag(request, tagged, tagged_for=None):
    tagged_by = request.user
    if not tagged_for:
        tagged_for = tagged_by
    tag_type = request.POST['tag_type']
    tag_value = request.POST['tag_value']

    tag, deleted = tag_delete(tagged, tag_type, tag_value, tagged_by)
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
        children = [plot_tag(tag, depth=depth-1) for tag in get_tags(tagged = resource, tagged_by = resource.user, tag_type = 'skill')]
    else:
        children = []
    return {  
        "id": resource.__class__.__name__ + "-" +str(resource.id),  
        "name": resource.name,  
        "children": children,
        "data": {'relation':"<h4>%s</h4>" %(resource.name)}
     }


@login_required
def map_tags(request, tagged):
    json = plot_resource(tagged, depth=2)
    json = simplejson.dumps(json)
    return HttpResponse(json, mimetype='application/json')
