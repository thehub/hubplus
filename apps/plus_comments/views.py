
from django.conf import settings

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required

from django.template import RequestContext

from threadedcomments.views import free_comment
from threadedcomments.models import ThreadedComment
from threadedcomments.forms import ThreadedCommentForm

# XXX we need to slot the legacy commenting into our permissionable, more ajaxy framework
# 1) make an explicit ajax submit comment handler which returns json (at the moment, "our_comment" is called 
# through ajax but doesn't use it
# 2) make the initial comment form also call it
# 3) js on the client to manage
 
#@secure_resource(obj_schema={'commented':[TgGroup,WikiPage,Resource]},                                              
#                 required_interfaces={'commented':['Viewer','Comment']},                             
#                 with_interfaces={'tagged':['Viewer','Comment']})                                                          
#def ajax_add_comment(request, commented, target_id, template_name="plus_comments/reply_form.html", **kwargs) :     

# actually this is not so easy. Basically requires a rewrite of the comments as the function free_comment takes 
# content_type and id, not an object

@login_required
def our_comment(request, content_type, content_id, target_id, template_name="plus_comments/reply_form.html", **kwargs) :

    if request.POST :
        if request.POST.has_key('parent_id') :
            parent_id = request.POST['parent_id']
        else :
            parent_id = None
        
        try :
            ret = free_comment(request, content_type=content_type, object_id=content_id, parent_id=parent_id, model=ThreadedComment, form_class=ThreadedCommentForm)
        except Exception, e :
            raise e

        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get(id=content_type)
        obj=ct.get_object_for_this_type(id=content_id)
        from apps.plus_feed.models import FeedItem
        FeedItem.post_COMMENT(request.user, obj)
        return ret

    else :
        return render_to_response(template_name, {
            'user' : request.user,
            'parent_id' : target_id,
            'url' : '/plus_comments/our_comment/%s/%s/%s/' % (content_type, content_id, target_id),
            }, context_instance=RequestContext(request))

