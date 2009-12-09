
from django.conf import settings
from utils import hub_name,  hub_name_plural, main_hub_name

def get_area(context):
    path = context.path.split('/')
    return path[1]

def get_group_or_hub_name(context) :
    area = get_area(context)
    if area == 'groups' :
        return 'Group'
    else :
        return hub_name()

def get_hub_app_name(theme) :
    if theme == 'psn' :
        return 'regions:groups'
    else :
        return 'hubs:groups'

def configs(context):
    # This function is a context processor to load the base.html template with some other standard 
    # values pulled from local_settings.py
    if get_area(context) in ['groups','regions','hubs'] :
        is_group_type = True
    else :
        is_group_type = False

    try:
        SETTINGS = {
            'COPYRIGHT_HOLDER' : settings.COPYRIGHT_HOLDER,
            'PROJECT_THEME': settings.PROJECT_THEME,
            'WELCOME_PAGE' : 'clients/%s/welcome.html' % settings.PROJECT_THEME,
            'INTRO_BAR' : 'clients/%s/intro_bar.html' % settings.PROJECT_THEME,
            "HOME_TABS" : 'home/clients/%s/tabbed_subs.html' % settings.PROJECT_THEME,
            'SITE_NAME' : settings.SITE_NAME,
            'SITE_NAME_SHORT': settings.SITE_NAME_SHORT,
            'SITE_NAME_SENTENCE': settings.SITE_NAME_SENTENCE and settings.SITE_NAME_SENTENCE.encode('utf-8') or settings.PROJECT_NAME,
            'HUB_NAME' : hub_name(),
            'HUB_NAME_PLURAL' : hub_name_plural(),
            "MAIN_HUB_NAME" : main_hub_name(),
            'PROJECT_NAME' : settings.PROJECT_NAME,

            'CONTACT_EMAIL':settings.CONTACT_EMAIL,

            'CURRENT_AREA': get_area(context),
            'GROUP_OR_HUB' : get_group_or_hub_name(context),
            'IS_GROUP_TYPE' : is_group_type,

            'SUPPORT_EMAIL' : settings.SUPPORT_EMAIL,
            'EXPLORE_NAME' : settings.EXPLORE_NAME, 
            'EXPLORE_SEARCH_TITLE' : settings.EXPLORE_SEARCH_TITLE,
            'MEMBER_SEARCH_TITLE' : settings.MEMBER_SEARCH_TITLE,
            'GROUP_SEARCH_TITLE' : settings.GROUP_SEARCH_TITLE,
            'HUB_SEARCH_TITLE' : settings.HUB_SEARCH_TITLE,
            'TAG_SEARCH_TITLE' : settings.TAG_SEARCH_TITLE,
            'SIDE_SEARCH_TITLE' : settings.SIDE_SEARCH_TITLE,
            'DEVELOPMENT': settings.DEVELOPMENT,
            'JS_VERSION_NO': settings.JS_VERSION_NO,
            'CSS_VERSION_NO':settings.CSS_VERSION_NO,
            'CSS_FILES':settings.CSS_FILES,
            'JS_FILES':settings.JS_FILES,
            'GROUPS_INTRO_BOX' : 'groups_intro_bar',
            'MEMBERS_INTRO_BOX' : 'clients/%s/intro_box.html' % settings.PROJECT_THEME,
            'EXPLORE_INTRO_BOX' : 'explore_intro_bar', 
            'HUBS_INTRO_BOX' : 'hubs_intro_bar',

            'HOST_INFO_FORM' : 'profiles/clients/%s/host_info.html' % settings.PROJECT_THEME,
            
            'HUB_APP_NAME' : get_hub_app_name(settings.PROJECT_THEME),

            'STATUS_COPY' : settings.STATUS_COPY,
            'GOOGLE_MAP_KEY' : settings.GOOGLE_MAP_KEY,

            }

        return SETTINGS
        
    except Exception, e:
        import ipdb
        #ipdb.set_trace()
        print e
        raise e
