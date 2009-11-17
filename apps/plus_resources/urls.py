from django.conf.urls.defaults import *


urlpatterns = patterns('',
                       url(r'^(?P<resource_name>.+)/edit_resource/$', 'apps.plus_resources.views.edit_resource', name='edit_Resource'),
                       url(r'^(?P<resource_name>.+)/view_resource/$', 'apps.plus_resources.views.view_resource', name='view_Resource'),
                       url(r'^(?P<resource_name>.+)/delete_stub/$', 'apps.plus_resources.views.delete_stub_resource', name='deletestub_Resource'),
                       )

