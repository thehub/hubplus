
from django.conf import settings

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required

from django.template import RequestContext

from threadedcomments.views import free_comment
from threadedcomments.models import ThreadedComment
from threadedcomments.forms import ThreadedCommentForm

@login_required
def our_comment(request, content_type, content_id, target_id, template_name="plus_comments/reply_form.html", **kwargs) :
    if request.POST :
        if request.POST.has_key('parent_id') :
            parent_id = request.POST['parent_id']
        else :
            parent_id = None
        
        try :
            return free_comment(request, content_type=content_type, object_id=content_id, parent_id=parent_id, model=ThreadedComment, form_class=ThreadedCommentForm)
        except Exception, e :
            print e
            import ipdb
            raise e
            #ipdb.set_trace()
    else :

        return render_to_response(template_name, {
            'user' : request.user,
            'parent_id' : target_id,
            'url' : '/plus_comments/our_comment/%s/%s/%s/' % (content_type, content_id, target_id),
            }, context_instance=RequestContext(request))


