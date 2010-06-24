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

from friends.forms import InviteFriendForm
from friends.models import FriendshipInvitation, Friendship

from microblogging.models import Tweet, TweetInstance, Following
from microblogging.views import get_tweets_for
from apps.plus_feed.models import FeedItem

from profiles.models import Profile, HostInfo
from profiles.forms import ProfileForm, HostInfoForm

from avatar.templatetags.avatar_tags import avatar

from apps.plus_lib.models import add_edit_key

from apps.plus_permissions.api import secure_resource, secure_wrap, TemplateSecureWrapper, PlusPermissionsNoAccessException, PlusPermissionsReadOnlyException, get_anon_user

from django.contrib.auth.decorators import login_required

from apps.plus_tags.models import  tag_add, tag_delete, get_tags, tag_autocomplete

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from itertools import chain
from django.template import defaultfilters
from apps.plus_explore.forms import SearchForm
from apps.plus_links.models import get_links_for

#from gravatar.templatetags.gravatar import gravatar as avatar

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from apps.plus_explore.views import plus_search, get_search_types, set_search_order
from apps.plus_lib.search import side_search_args, listing_args

def narrow_search_types():
    types = dict(get_search_types())
    return (('Profile', types['Profile']),)

def profiles(request, tag_string='', template_name="plus_explore/explore_filtered.html"):
    form = SearchForm(request.GET)
    if form.is_valid():
        search, order = set_search_order(request, form)
    else:
        search = ''
        order = ''

    search_types = narrow_search_types()
    side_search = side_search_args('profile_list', search_types[0][1][2])

    head_title = _('Members')
    listing_args_dict = listing_args('profile_list', 'profile_list_tag', tag_string=tag_string, search_terms=search, multitabbed=False, order=order, template_base="site_base.html", search_type_label=head_title)
    search_dict = plus_search(listing_args_dict['tag_filter'], search, search_types, order)

    #users = users.filter(~Q(username='admin')).filter(~Q(username='anon')).filter(~Q(username='webapi'))
    return render_to_response(template_name, {'head_title':head_title, 
                                              'listing_args':listing_args_dict,
                                              'search_args':side_search,
                                              'search':search_dict,
                                              'intro_box_override':True}, context_instance=RequestContext(request))



def show_section(profile, attribute_list) :
    # if none of the list of attributes are visible to this viewer, hide them all
    def test_att(name) :
        if profile.__getattr__('should_show_'+name) :
            return True
        return False

    return any((test_att(name) for name in attribute_list))



#from settings import trellis

def hello(a):
    print `a` * 20



def profile(request, username, template_name="profiles/profile.html"):
    #trellis.callInEventLoop(hello, "Tom")

    is_me = False
    user = request.user


    if request.user.is_authenticated() :
        if user.username == username :
            is_me = True
    else :
        user = get_anon_user()

    other_user = secure_wrap(get_object_or_404(User, username=username),user)

    is_following = Following.objects.is_following(request.user, other_user.get_inner())

    p = other_user.get_inner().get_profile()
    profile = secure_wrap(p,user)
    profile.user # trigger permission exception if no access
 
    can_change_avatar = False
    
    try :
        profile.change_avatar
        can_change_avatar = True
    except PlusPermissionsNoAccessException :
        pass

    interests = get_tags(tagged=other_user.get_inner().get_profile(), 
                         tagged_for=other_user.get_inner(), tag_type='interest')
    skills = get_tags(tagged = other_user.get_inner().get_profile(), 
                      tagged_for=other_user.get_inner(), tag_type='skill')
    needs = get_tags(tagged = other_user.get_inner().get_profile(), 
                     tagged_for=other_user.get_inner(), tag_type='need')

    user_type = ContentType.objects.get_for_model(other_user)

    # new style statuses
    tweets = FeedItem.feed_manager.get_from(other_user.get_inner()).order_by("-sent")
    if tweets :
        latest_status = tweets[0]
        status_since = defaultfilters.timesince(latest_status.sent)
    else:
        status_since = ''
    status_type = 'profile'

    try:
        profile.get_all_sliders
        perms_bool = True
    except PlusPermissionsNoAccessException:
        perms_bool = False

    profile = TemplateSecureWrapper(profile)

    search_type = 'profile_list' 
    search_types = narrow_search_types()
    search_types_len = len(search_types)
    search_type_label = search_types[0][1][2]


    host_info = p.get_host_info()
    host_info = secure_wrap(host_info, user, interface_names=['Viewer', 'Editor'])

    see_host_info = False
    try :
        host_info.user 
        see_host_info = True
    except :
        pass # can't see host_info
    host_info = TemplateSecureWrapper(host_info)
    
    hubs = other_user.get_inner().hubs()
    non_hub_groups = [(g.group_app_label() + ':group', g) for g in 
                      other_user.get_inner().groups.filter(level='member').exclude(id__in=hubs)]
    hubs = [(g.group_app_label() + ':group', g) for g in hubs]

    see_about = is_me or show_section(profile, ('about',))
    see_contacts = is_me or show_section(profile,('mobile','home','work','fax','website','address','email_address'))
    
    see_links = is_me
    links = get_links_for(other_user,RequestContext(request))
    if links :
        see_links = True

    can_tag = profile.has_interface('Profile.Editor')


    template_args = {
            "is_me": is_me,
            "is_following": is_following,
            "other_user": other_user.get_inner(), # XXX - should fix this get_inner
            "profile":profile,
            "can_change_avatar":can_change_avatar,

            "head_title" : "%s" % profile.get_display_name(),
            "status_type" : status_type,
            "status_since" : status_since,
            "host_info" : host_info,
            "skills" : skills,
            "needs" : needs,
            "interests" : interests,
            "other_user_tweets" : tweets,
            "permissions":perms_bool,
            "non_hub_groups":non_hub_groups,
            "hubs":hubs,
            "search_type":search_type,
            "search_types":search_types,
            "search_type_label":search_type_label,
            "search_types_len":search_types_len,
            "host_info":host_info, 
            "see_host_info":see_host_info,
            "see_about":see_about,
            "see_contacts":see_contacts,
            "see_links":see_links,
            "other_user_class":user_type.id,
            "other_user_id":other_user.id,
            "can_tag":can_tag,
            }
    labels = {'MAIN_HUB_LABEL':_('Main %s')%settings.HUB_NAME,
              'MAIN_HUB_DEFAULT':_("No %s selected")%settings.HUB_NAME}
    template_args.update(labels)

    return render_to_response(template_name, template_args, context_instance=RequestContext(request))

def our_profile_permission_test(fn) :
    """ Trying to put our permission testing into a decorator """
    def our_fn(request,username,*args,**kwargs) :
        other_user = get_object_or_404(User,username=username)
        profile = other_user.get_profile()
        if not has_access(request.user,profile,'Profile.Viewer') :
            return HttpResponse("You don't have permission to do that to %s, you are %s" % (username,request.user),status=401)
        else :
            return fn(request, username, *args, **kwargs)
    return our_fn

def name_to_profile(fn):
    def our_fn(request,username,*args,**kwargs):
        other_user = get_object_or_404(User,username=username)
        return fn(request, other_user.get_profile(), *args, **kwargs)
    return our_fn
    
    

@login_required
def update_profile_form(request,username) :
    """ Get a prefilled basic form for the profile """
    other_user = get_object_or_404(User,username=username)
    p = other_user.get_profile()
    if not has_access(request.user,p,'Profile.Viewer') :
        raise PlusPermissionsNoAccessException(Profile,p.pk,'update_profile_form')
    else :
        profile_form = ProfileForm(request.POST, p)


@login_required
@secure_resource(User)
def profile_field(request, other_user, classname, fieldname, *args, **kwargs) :
    """ Get the value of one field from the user profile, so we can write an ajaxy editor """
    print "In profile_field"
    print "username %s, classname %s, fieldname %s" % (other_user.username,classname,fieldname)
    p = secure_wrap(other_user.get_profile(), request.user)

    if classname == 'Profile' :
        return one_model_field(request, p, ProfileForm, fieldname, kwargs.get('default', ''),[p.user])
    elif classname == 'HostInfo' :
        return one_model_field(request, p.get_host_info(), HostInfoForm, fieldname, kwargs.get('default', ''), [p.user])


def one_model_field(request, object, formClass, fieldname, default, other_objects=None) :
    val = getattr(object, fieldname)
    if not request.POST:
        if not val:
            val = ""
        return HttpResponse("%s" % val, mimetype="text/plain")

    field_validator = formClass.base_fields[fieldname]
    new_val = request.POST['value']
    try:
        field_validator.clean(new_val)
    except ValidationError, e:
        return HttpResponse('%s' % e, status=500)

    try:
        setattr(object, fieldname, new_val)
        object.save()
        if other_objects :
            for o in other_objects :
                o.save()
    except Exception, e :
        return HttpResponse('%s' % e, status=500)
    new_val = new_val and new_val or default
    return HttpResponse("%s" % new_val, mimetype='text/plain')

@login_required
def get_main_permission_sliders(request,username):
    """XXX NEEDS REWRITING"""
    return HttpResponse(MAKE_MY_JSON_FOR_THIS, mimetype='text/plain')

def content_object(c_type, c_id) :
    a_type = ContentType.objects.get_for_id(c_type)
    return a_type.get_object_for_this_type(pk=c_id)



@login_required
def update_main_permission_sliders(request,username) :
    """XXX REWRITE"""
    pass



@login_required
def autocomplete_user_or_full_name(request):
    """ looks for user and fullname  """

    q = request.GET['q']

    limit = request.GET['limit']             
    if not limit :
        limit = 40 # should be enough for anyone
    q_username = Q(user__username__istartswith=q)
    q_first = Q(user__first_name__istartswith=q)
    q_last = Q(user__last_name__istartswith=q)
    
    query = q_username | q_first | q_last
    if ' ' in q :
        first,rest = q.split(' ')
        q_full = Q(user__first_name__istartswith=first,user__last_name__istartswith=rest)
        query = query | q_full

    options = ['%s %s (%s)' % (p.user.first_name, p.user.last_name, p.user.username) for p in Profile.objects.filter(query)[:limit]] 

    # XXX add permissioning on results

    options = '\n'.join(options)
    return HttpResponse(options)
