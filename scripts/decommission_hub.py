
# things to do to decommission a hub

# identify all members
# remove them from both the hub and the hosting group
# if they're not a member of anything else, deactivate them
# delete the hub


from django.contrib.auth.models import User
from apps.plus_groups.models import TgGroup
from apps.plus_permissions.default_agents import get_all_members_group, get_removed_user
from django.contrib.contenttypes.models import ContentType


import apps.plus_feed.models as feed_models
feed_models.FEED_ON = False

import hashlib

from datetime import datetime

all_members = get_all_members_group()
removed_user = get_removed_user()

from string import ascii_uppercase, ascii_lowercase

from apps.plus_feed.models import FeedItem

 
def rot13(data):
    """ A simple rot-13 encoder since `str.encode('rot13')` was removed from
        Python as of version 3.0.  It rotates both uppercase and lowercase letters individually.
    """
    total = []
    for char in data:
        if char in ascii_uppercase:
            index = (ascii_uppercase.find(char) + 13) % 26
            total.append(ascii_uppercase[index])
        elif char in ascii_lowercase:
            index = (ascii_lowercase.find(char) + 13) % 26
            total.append(ascii_lowercase[index])
        else:
            total.append(char)
    return "".join(total)


def mangle(s) :
    print s
    #s = hashlib.sha1()
    #s.update(user.username)
    #s.update('%s'%datetime.now())
    #user.username = s.digest()
    #s.update(user.email_address)
    #user.email_address = s.digest()
    s2 = 'XX%s'% rot13(s)
    print s,s2
    return s2



def hide_user(user) :
    user.username = mangle(user.username)
    user.email_address = mangle(user.email_address)

    user.active = False

    user.description = ''
    user.organization = ''
    user.mobile = ''
    user.home = ''
    user.work = ''
    user.fax = ''
    user.place = ''
    user.skype_id = ''
    user.website = ''
    user.address = ''
    user.country = ''
    user.homehub = None
    user.post_or_zip = ''

    # remove FeedItem
    for fi in FeedItem.feed_manager.get_from(user) :
        fi.source = removed_user.get_ref()
        fi.save()


    # creator of pages
    from apps.plus_resources.models import Resource
    from apps.plus_wiki.models import WikiPage

    for p in WikiPage.objects.created_by(user) :
        p.created_by = removed_user
        p.save()
    
    # uploads
    for r in Resource.objects.created_by(user) :
        r.created_by = removed.user
        r.save()

    # remove following statuses
        for f in Following.objects.filter(follower_content_type=content_type,follower_object_id=self.id) :
            f.delete()
        for f in Following.objects.filter(followed_content_type=content_type,followed_object_id=self.id) :
            f.delete()

            
    # remove comments                                                                                                
    from threadedcomments.models import ThreadedComment
    content_type = ContentType.objects.get_for_model(user)
    for c in ThreadedComment.objects.filter(content_type=content_type, object_id=user.id) :
        c.user = removed_user
        c.save()


    user.save()

    


def decommission(group) :
    break_flag = False
    members = [m for m in group.get_members() if m.is_user()]
    kill_list = []
    save_list = []
    print members
    for m in members :
        print '+',m.id,m,
        if m.username == 'fgodat' :
            continue
        enc = m.get_enclosures()
        hub_types = [e for e in enc if e.is_hub_type() and e != all_members]
        print hub_types
        if len(hub_types)==1 and hub_types[0]==group :
            kill_list.append(m)
            #break_flag = True
        else :
            save_list.append(m)

        group.remove_member(m)
        if break_flag :
            break
        
    print "Killed"
    print kill_list
    print "Saved"
    print save_list
                
    for u in kill_list :
        hide_user(u)
        
         
    #group.place.hidden = True
    #group.place.save()
                        
    
def decommission_it(group_id) :
    group = TgGroup.objects.get(id=group_id)
    hosts = group.get_admin_group()
    decommission(group)
    #decommission(hosts)

    

decommission_it(22)

