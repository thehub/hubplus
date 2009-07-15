from django.shortcuts import render_to_response, get_object_or_404

from apps.plus_permissions.models import PermissionSystem, get_permission_system
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import simplejson
from models import *
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden

# this collection must be kept up-to-date for each type of model which 
# CHANGE THIS
from apps.profiles.models import Profile
from apps.hubspace_compatibility.models import TgGroup

from django.contrib.contenttypes.models import ContentType

def tag_permission_test(fn) :
    """ Decorator for permissions for adding and removing tags. """
    def our_fn(request,*args,**kwargs) :
        print "AAA"
        ps = get_permission_system()
        print "BBB"
        target_class = request.POST['target_class']
        target_id = request.POST['target_id']
        print "CCC %s, %s" % (target_class,target_id)

        if target_id != '' and target_class != '' :
            try :
                cls = eval(target_class)
            except Exception, e :
                print "error evaling target_class %s : $%s$" % (target_class,e)
            tagged_resource = get_object_or_404(cls,pk=target_id)
        else :
            tagged_resource = None
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
    target_class = request.POST['target_class']
    target_id = request.POST['target_id']
    tagger = request.user
    tag, added = tag_add(tagged_resource, tag_type, tag_value, tagger)
    data = simplejson.dumps({'keyword':tag.keyword, 'tag_type':tag.tag_type, 'tagged':'yourself', 'added':added})
    return HttpResponse(data, mimetype='application/json')

@login_required
#@tag_permission_test
@transaction.commit_on_success
def autocomplete_tag(request, tag_type, target_class, target_id):
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

@login_required
@tag_permission_test
def map_tags(request, tagged_resource):
    json = {
         "id": tagged_resource.__class__.__name__ + "-" +str(tagged_resource.id),
         "name": tagged_resource.name,
         "children": [{"id": 'tag' + "-" +str(tag.id),
                       "name": tag.keyword,
                       "data": {
                           'relation': "<h4>%s tagged as %s</h4> " %(tagged_resource.name, tag.keyword)
                           },
                       "children": []} for tag in get_tags(tagged = tagged_resource, tagger = request.user, tag_type = 'skill')],
         "data": {'relation':"<h4>%s</h4>" %(tagged_resource.name)}
     }

    json = simplejson.dumps(json)
    return HttpResponse(json, mimetype='application/json')
