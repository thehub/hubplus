from django.conf.urls.defaults import *


urlpatterns = patterns('',

    url(r'^(?P<resource_id>[\d]+)/upload/$', 'apps.plus_resources.views.edit_resource', name='edit_Resource'),

)

