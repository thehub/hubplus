from django.conf.urls.defaults import *
from account.forms import *

urlpatterns = patterns('',
    url(r'^settings/$','account.views.site_settings', name='acct_settings'),                       
    url(r'^email/$', 'account.views.email', name="acct_email"),
    #url(r'^signup/$', 'account.views.signup', name="acct_signup"),
    url(r'^signup/invited/(?P<resource_id>[0-9]+)/$', 'apps.account.views.proxied_invited_signup', name='proxied_invited_signup'),
    url(r'^signup/(?P<resource_id>[0-9]+)/$', 'apps.account.views.proxied_signup', name='proxied_signup'),
    url(r'^login/$', 'account.views.login', name="acct_login"),
    url(r'^fast_login/$', 'account.views.fast_login', name='acct_fast_login'),
    url(r'^login/openid/$', 'account.views.login', {'associate_openid': True},
        name="acct_login_openid"),
    url(r'^password_change/$', 'account.views.password_change', name="acct_passwd"),
    url(r'^password_set/$', 'account.views.password_set', name="acct_passwd_set"),
    url(r'^password_delete/$', 'account.views.password_delete', name="acct_passwd_delete"),
    url(r'^password_delete/done/$', 'django.views.generic.simple.direct_to_template', {
        "template": "account/password_delete_done.html",
    }, name="acct_passwd_delete_done"),
    url(r'^password_reset/$', 'account.views.password_reset', name="acct_passwd_reset"),
    url(r'^timezone/$', 'account.views.timezone_change', name="acct_timezone_change"),
    url(r'^other_services/$', 'account.views.other_services', name="acct_other_services"),
    url(r'^other_services/remove/$', 'account.views.other_services_remove', name="acct_other_services_remove"),
    
    url(r'^language/$', 'account.views.language_change', name="acct_language_change"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {"template_name": "account/logout.html"}, name="acct_logout"),
    
    url(r'^confirm_email/(\w+)/$', 'emailconfirmation.views.confirm_email', name="acct_confirm_email"),

    url(r'^apply/$', 'account.views.apply', name='acct_apply'),
    url(r'^site_invite/$', 'account.views.site_invite', name='acct_invite'),
    # Setting the permanent password after getting a key by email
    url(r'^password_reset_key/(\w+)/$', 'account.views.password_reset_from_key', name="acct_passwd_reset_key"),
    url(r'^(?P<resource_id>[0-9]+)/$', 'account.views.proxied_signup', name='proxied_signup'),
    # ajax validation
    (r'^validate/$', 'ajax_validation.views.validate', {'form_class': SignupForm}, 'signup_form_validate'),
)
