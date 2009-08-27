from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models.signals import post_syncdb

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        print "creating plus_contact notice types"
        notification.create_notice_type("new_application", "New application to the site.", "Someone has applied to join hubplus")
        notification.create_notice_type("application_approved", "Application Approved", "An application was approved")

    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
