import os.path

from avatar.models import Avatar, avatar_file_path
from avatar.forms import PrimaryAvatarForm, DeleteAvatarForm
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from django.contrib.auth.models import User

from apps.plus_permissions.models import GenericReference
from apps.plus_groups.models import TgGroup
from django.conf import settings

from apps.plus_lib.utils import hub_name
def _get_next(request):
    """
    The part that's the least straightforward about views in this module is how they 
    determine their redirects after they have finished computation.

    In short, they will try and determine the next place to go in the following order:

    1. If there is a variable named ``next`` in the *POST* parameters, the view will
    redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, the view will
    redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, the view will
    redirect to that previous page.
    """
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    if not next:
        next = request.path
    return next


@login_required
def change_user_avatar(request, username, **kwargs):
    target_obj = get_object_or_404(User, username=username)
    return change_avatar(request, target_obj, 'user', 'Profile', **kwargs)

@login_required
def change_group_avatar(request, group_id, **kwargs) :
    target_obj = get_object_or_404(TgGroup, id=group_id)
    if target_obj.is_hub_type() :
        from_name = hub_name()
    else :
        from_name = 'Group'

    return change_avatar(request, target_obj, 'group', from_name, **kwargs)


def change_avatar(request, target_obj, target_type, from_name, extra_context={}, 
                  next_override=None, current_app='plus_groups',namespace='groups',**kwargs):

    # XXX some of this should probably be refactored into the model layer 
    target = target_obj.get_ref()
    avatars = Avatar.objects.filter(target=target).order_by('-primary')
    if avatars.count() > 0:
        avatar = avatars[0]
        kwargs = {'initial': {'choice': avatar.id}}
    else:
        avatar = None
        kwargs = {}

    primary_avatar_form = PrimaryAvatarForm(request.POST or None, target=target, **kwargs)
    if request.method == "POST":
        if 'avatar' in request.FILES:
            path = avatar_file_path(target=target, 
                filename=request.FILES['avatar'].name)
            avatar = Avatar(
                target = target,
                primary = True,
                avatar = path,
            )
            new_file = avatar.avatar.storage.save(path, request.FILES['avatar'])
            avatar.save()
            request.user.message_set.create(
                message=_("Successfully uploaded a new avatar."))
        if 'choice' in request.POST and primary_avatar_form.is_valid():
            avatar = Avatar.objects.get(id=
                primary_avatar_form.cleaned_data['choice'])
            avatar.primary = True 
            avatar.save()
            
            request.user.message_set.create(
                message=_("Successfully updated your avatar."))
        return HttpResponseRedirect(next_override or _get_next(request))

    return render_to_response(
        'avatar/change.html',
        extra_context,
        context_instance = RequestContext(
            request,
            { 'avatar': avatar, 
              'avatars': avatars,
              'primary_avatar_form': primary_avatar_form,
              'next': next_override or _get_next(request),
              'target' : target_obj,
              'target_type' : target_type,
              'from_name' : from_name,
              }
        )
    )


@login_required
def delete(request, extra_context={}, next_override=None):
    avatars = Avatar.objects.filter(target=request.user.get_ref()).order_by('-primary')
    if avatars.count() > 0:
        avatar = avatars[0]
    else:
        avatar = None
    delete_avatar_form = DeleteAvatarForm(request.POST or None, user=request.user)
    if request.method == 'POST':
        if delete_avatar_form.is_valid():
            ids = delete_avatar_form.cleaned_data['choices']
            Avatar.objects.filter(id__in=ids).delete()
            request.user.message_set.create(
                message=_("Successfully deleted the requested avatars."))
            return HttpResponseRedirect(next_override or _get_next(request))
    return render_to_response(
        'avatar/confirm_delete.html',
        extra_context,
        context_instance = RequestContext(
            request,
            { 'avatar': avatar, 
              'avatars': avatars,
              'delete_avatar_form': delete_avatar_form,
              'next': next_override or _get_next(request), }
        )
    )




def get_url(request, username) :
    from apps.avatar.templatetags.avatar_tags import avatar_url
    from django.contrib.auth.models import User
    try :
        user = User.objects.get(username=username)
        return HttpResponse("%s" % avatar_url(user), mimetype='text/plain')
    except :
        raise Http404('File does not exist')



def get_avatar(request, username, size=100) :    
    from apps.plus_lib.lighttpd_serve import send_file, get_mimetype, get_size, \
         get_last_modified, file_exists, SITE_MEDIA_ROOT, WEBSERVER_MEDIA_ROOT

    user = get_object_or_404(User, username=username)

    try :
        avatar = Avatar.objects.get_for_target(user)
        if not avatar.thumbnail_exists(size) :
            avatar.create_thumbnail(int(size))
     
 
        file_path = SITE_MEDIA_ROOT +'/'+avatar.avatar_name(size)
        lightty_path = WEBSERVER_MEDIA_ROOT + avatar.avatar_name(size)

        file_size = get_size(file_path)
        mimetype = get_mimetype(file_path)
        last_modified = get_last_modified(file_path)
        
        new_filename=avatar.avatar.file.name.split('/')[-1]  
        content_disposition = 'attachment;filename=%s'%new_filename
        
        print file_size, lightty_path, mimetype, last_modified, content_disposition
        return send_file(lightty_path, file_size, mimetype, last_modified, content_disposition)

    except Avatar.DoesNotExist :
        return HttpResponseRedirect('/site_media/images/member.jpg')
