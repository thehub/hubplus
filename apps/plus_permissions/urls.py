
from django.conf.urls.defaults import *


urlpatterns = patterns('',
                       url(r'^patch_in_profiles$', 'plus_permissions.views.patch_in_profiles', name='profile_list')
                       )
