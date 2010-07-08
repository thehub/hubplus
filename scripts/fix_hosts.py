from django.contrib.auth.models import User
from apps.plus_groups.models import TgGroup

from apps.plus_permissions.models import get_all_members_group
from django.conf import settings

import apps.plus_feed.models as feed_models

all_members = get_all_members_group()
site_admin = all_members.get_admin_group()

rot = TgGroup.objects.get(id=31)
rot_ads = rot.get_admin_group()

real_hosts = ['moraan.gilad', 'lieke.smeets','victor.hanenburg','marieke.verhoeven',
              'nicolas.eizaguirre','jessica.curta','joris.martens','ursel.biester',
              'tineke.molendijk','gilbert.nijs']


feed_models.FEED_ON = False

def clean() :
    for u in rot_ads.get_members() :
        if u.is_user() and u.username not in real_hosts :
            print u
            rot_ads.remove_member(u)

        if u.is_group() :
            print u


clean()
