from django.conf.urls.defaults import *


urlpatterns = patterns('',

    url(r'^(?P<resource_id>[\d]+)/upload/$', 'apps.plus_resources.views.upload_resource', name='upload_resource'),

)

