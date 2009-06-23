from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'apps.synced.login', name="acct_login"),
)
