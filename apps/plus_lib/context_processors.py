
from django.conf import settings
from utils import hub_name,  hub_name_plural

def get_area(context):
    segment = context.path.split('/')[0]

def configs(context):
    # This function is a context processor to load the base.html template with some other standard 
    # values pulled from local_settings.py
    try:
        SETTINGS = {
            'COPYRIGHT_HOLDER' : settings.COPYRIGHT_HOLDER,
            'PROJECT_THEME': settings.PROJECT_THEME,
            'WELCOME_PAGE' : 'clients/%s/welcome.html' % settings.PROJECT_THEME,
            'site_name' : settings.PROJECT_NAME,
            'HUB_NAME' : hub_name(),
            'HUB_NAME_PLURAL' : hub_name_plural(),
            'PROJECT_NAME' : settings.PROJECT_NAME,
            'current_area': get_area(context)
            }

        return SETTINGS
        
    except Exception, e:
        import ipdb
        ipdb.set_trace()
