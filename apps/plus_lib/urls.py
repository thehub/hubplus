from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(r'^(?P<resource_id>[\w\._-]+)/field/(?P<classname>[\w_]+)/(?P<fieldname>[\w_]+)/(?P<default>[\w_]*)$','plus_lib.views.field',
           {},name='field'),
)

