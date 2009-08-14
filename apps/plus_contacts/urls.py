from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^list_open_applications/$', 'apps.plus_contacts.views.list_of_applications', name='list_open_applications'),
    url(r'^accept_application/(?P<id>[0-9]+)/$', 'apps.plus_contacts.views.accept_application', name='accept_application'),
    url(r'^signup/(?P<key>[\w-]+)/$', 'apps.signup.views.signup', name='key_signup'),
)
