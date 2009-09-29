from django.conf.urls.defaults import *


urlpatterns = patterns('',

    url(r'^(?P<resource_name>.+)/edit_resource/$', 'apps.plus_resources.views.edit_resource', name='edit_Resource'),

)

