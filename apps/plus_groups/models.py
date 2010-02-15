from django.db import models
from django.db.models.signals import post_save
from itertools import chain
from django.contrib.auth.models import User, UserManager, check_password
from django.conf import settings

from apps.plus_contacts.status_codes import ACCEPTED_PENDING_USER_SIGNUP
from apps.plus_permissions.proxy_hmac import attach_hmac 


from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from apps.plus_lib.status import StatusDescriptor
from django.contrib.contenttypes.models import ContentType

from django.template import Template, Context
from django.contrib.contenttypes import generic

class Location(models.Model):
    class Meta:
        db_table = u'location'

    name = models.CharField(unique=True, max_length=200)


#patch django orm's "create_many_related_manager"
from django.db.models.fields.related import *
import django.db.models.fields.related


def create_many_related_manager(superclass, through=False):
    """Creates a manager that subclasses 'superclass' (which is a Manager)
    and adds behavior for many-to-many related objects."""
    class ManyRelatedManager(superclass):
        def __init__(self, model=None, core_filters=None, instance=None, symmetrical=None,
                join_table=None, source_col_name=None, target_col_name=None):
            super(ManyRelatedManager, self).__init__()
            self.core_filters = core_filters
            self.model = model
            self.symmetrical = symmetrical
            self.instance = instance
            self.join_table = join_table
            self.source_col_name = source_col_name
            self.target_col_name = target_col_name
            self.through = through
            self._pk_val = self.instance._get_pk_val()
            if self._pk_val is None:
                raise ValueError("%r instance needs to have a primary key value before a many-to-many relationship can be used." % instance.__class__.__name__)

        def get_query_set(self):
            return superclass.get_query_set(self)._next_is_sticky().filter(**(self.core_filters))

        # If the ManyToMany relation has an intermediary model,
        # the add and remove methods do not exist.

        def add(self, *objs):
            self._add_items(self.source_col_name, self.target_col_name, *objs)
            
                # If this is a symmetrical m2m relation to self, add the mirror entry in the m2m table
            if self.symmetrical:
                self._add_items(self.target_col_name, self.source_col_name, *objs)
        add.alters_data = True

        def remove(self, *objs):
            self._remove_items(self.source_col_name, self.target_col_name, *objs)
                
                # If this is a symmetrical m2m relation to self, remove the mirror entry in the m2m table
            if self.symmetrical:
                self._remove_items(self.target_col_name, self.source_col_name, *objs)
        remove.alters_data = True

        def clear(self):
            self._clear_items(self.source_col_name)

            # If this is a symmetrical m2m relation to self, clear the mirror entry in the m2m table
            if self.symmetrical:
                self._clear_items(self.target_col_name)
        clear.alters_data = True

        def create(self, **kwargs):
            # This check needs to be done here, since we can't later remove this
            # from the method lookup table, as we do with add and remove.
            new_obj = super(ManyRelatedManager, self).create(**kwargs)
            self.add(new_obj)
            return new_obj
        create.alters_data = True

        def get_or_create(self, **kwargs):
            obj, created = \
                    super(ManyRelatedManager, self).get_or_create(**kwargs)
            # We only need to add() if created because if we got an object back
            # from get() then the relationship already exists.
            if created:
                self.add(obj)
            return obj, created
        get_or_create.alters_data = True

        def _add_items(self, source_col_name, target_col_name, *objs):
            # join_table: name of the m2m link table
            # source_col_name: the PK colname in join_table for the source object
            # target_col_name: the PK colname in join_table for the target object
            # *objs - objects to add. Either object instances, or primary keys of object instances.

            # If there aren't any objects, there is nothing to do.
            if objs:
                # Check that all the objects are of the right type
                new_ids = set()
                for obj in objs:
                    if isinstance(obj, self.model):
                        new_ids.add(obj._get_pk_val())
                    else:
                        new_ids.add(obj)
                # Add the newly created or already existing objects to the join table.
                # First find out which items are already added, to avoid adding them twice
                cursor = connection.cursor()
                cursor.execute("SELECT %s FROM %s WHERE %s = %%s AND %s IN (%s)" % \
                    (target_col_name, self.join_table, source_col_name,
                    target_col_name, ",".join(['%s'] * len(new_ids))),
                    [self._pk_val] + list(new_ids))
                existing_ids = set([row[0] for row in cursor.fetchall()])

                # Add the ones that aren't there already
                for obj_id in (new_ids - existing_ids):
                    cursor.execute("INSERT INTO %s (%s, %s) VALUES (%%s, %%s)" % \
                        (self.join_table, source_col_name, target_col_name),
                        [self._pk_val, obj_id])
                transaction.commit_unless_managed()

        def _remove_items(self, source_col_name, target_col_name, *objs):
            # source_col_name: the PK colname in join_table for the source object
            # target_col_name: the PK colname in join_table for the target object
            # *objs - objects to remove

            # If there aren't any objects, there is nothing to do.
            if objs:
                # Check that all the objects are of the right type
                old_ids = set()
                for obj in objs:
                    if isinstance(obj, self.model):
                        old_ids.add(obj._get_pk_val())
                    else:
                        old_ids.add(obj)
                # Remove the specified objects from the join table
                cursor = connection.cursor()
                cursor.execute("DELETE FROM %s WHERE %s = %%s AND %s IN (%s)" % \
                    (self.join_table, source_col_name,
                    target_col_name, ",".join(['%s'] * len(old_ids))),
                    [self._pk_val] + list(old_ids))
                transaction.commit_unless_managed()

        def _clear_items(self, source_col_name):
            # source_col_name: the PK colname in join_table for the source object
            cursor = connection.cursor()
            cursor.execute("DELETE FROM %s WHERE %s = %%s" % \
                (self.join_table, source_col_name),
                [self._pk_val])
            transaction.commit_unless_managed()

    return ManyRelatedManager

django.db.models.fields.related.create_many_related_manager = create_many_related_manager


try :
    class TgGroup(models.Model):
        
        class Meta:
            db_table = u'tg_group'
            ordering = ['display_name']
            
        #users = models.ManyToManyField(User, through="User_Group") #'groups' attribute is removed in plus_user.models

#through="User_Group" stops the add and remove functionality unnecessarily. Above we patch it back in. 
                                                                   #The reverse lookup of "user.groups" unfortunately still doesn't work, however you can get a reverse lookup on user.user_group_set from which the results could be inferred
                                                                   #db_table="user_group" doesn't use the right columns for lookup

        group_name = models.CharField(unique=True, max_length=70)
        display_name = models.CharField(max_length=255)
        created = models.DateTimeField(auto_now_add=True)

        address = models.CharField(max_length=255, null=True)

        place = models.ForeignKey(Location)
    #if place is Hub Islington then set member of toHub Islington group if level is member
    #if level is host, set member of to Hub Islington Host Group.
        level = models.CharField(max_length=9)
        psn_id = models.CharField(max_length=100)
        path = models.CharField(max_length=120)

        child_groups = models.ManyToManyField('self', symmetrical=False, related_name='parent_groups')
       
        #  getting rid of "about" as there's no data in it from hubspace and we're using "description"
        #about = models.TextField('about', null=True, blank=True)

        group_type = models.CharField('type', max_length=20, choices=settings.GROUP_TYPES)
    
        title = models.CharField(max_length=60)
        description = models.TextField()

        def content(self):
            return self.body
        body = models.TextField()
        rights = models.TextField()

        active = models.BooleanField()

        status = StatusDescriptor() 

        def post_join(self, user_or_group) :
            """ this method, a break out of other stuff which happens when members join groups,
            can be called as an independent funtion from syncer"""

            # add host permissions on profile when join/leave Hub
            from apps.plus_permissions.types.Profile import ProfileInterfaces
            from apps.plus_permissions.default_agents import get_all_members_group, get_admin_user
            admin = get_admin_user()
            admin_group = self.get_admin_group()
            if self.group_type == 'hub':
                for prof in ProfileInterfaces:
                    user_or_group.get_security_context().add_arbitrary_agent(admin_group, 'Profile.%s' % prof, admin)

            from apps.microblogging.models import send_tweet # avoid circularity                                         
            message = _("%(joiner)s joined the group %(group)s") % (
                {'joiner':user_or_group.get_display_name(),'group':self.get_display_name()})
            send_tweet(user_or_group, message)

            
        def add_member(self, user_or_group):
            if isinstance(user_or_group, User) and not self.users.filter(id=user_or_group.id):
                from apps.plus_permissions.types.Profile import ProfileInterfaces
                self.users.add(user_or_group)

                self.post_join(user_or_group)

            if isinstance(user_or_group, self.__class__) and not self.child_groups.filter(id=user_or_group.id):
                self.child_groups.add(user_or_group)


        def join(self, user):
            self.add_member(user)
            return user

        def apply(self, user, applicant=None, about_and_why=''):
            if not applicant:
                raise ValueError('there must be an applicant')
            self.create_Application(user, 
                                    applicant=applicant, 
                                    request=about_and_why, 
                                    group=self)


        def invite_member(self, user, invited, message=''):
            if not invited:
                raise ValueError('there must be an invitee')

            invite = self.create_MemberInvite(user,
                                              invited=invited, 
                                              invited_by=user, 
                                              group=self, 
                                              status=ACCEPTED_PENDING_USER_SIGNUP)


        def change_avatar(self) :
            pass

        def leave(self, user):
            return self.remove_member(user)

        def message_members(self, sender, message_header, message_body, domain) :
            from apps.plus_lib.utils import message_user
            for member in self.get_users() :
                message_user(sender, member, message_header, message_body, domain)

        def is_group(self) : return True

        def post_leave(self, user_or_group) :
            """ this method, a break out of other stuff which happens when members leave groups,
            can be called as an independent function from syncer"""

            from apps.plus_permissions.types.Profile import ProfileInterfaces
            from apps.plus_permissions.default_agents import get_all_members_group, get_admin_user
            # remove host erpermissions on profile when join/leave Hub
            admin = get_admin_user()
            admin_group = self.get_admin_group()
            if self.group_type == 'hub':
                for prof in ProfileInterfaces:
                    user_or_group.get_security_context().remove_arbitrary_agent(admin_group, 'Profile.%s' % prof, admin)

            from apps.microblogging.models import send_tweet
            message = _("%(leaver)s left the group %(group)s") % (
                {'leaver':user_or_group.get_display_name(),'group':self.get_display_name()})
            send_tweet(user_or_group, message)
            
            # if I was the homehome for this user, change
            if user_or_group.homehub == self :
                user_or_group.homehub = get_all_members_group()
                user_or_group.save()


        def remove_member(self, user_or_group):
            if isinstance(user_or_group, User) and self.users.filter(id=user_or_group.id):
                self.users.remove(user_or_group)
                self.post_leave(user_or_group)

            if isinstance(user_or_group, self.__class__) and self.child_groups.filter(id=user_or_group.id):
                self.child_groups.remove(user_or_group)


        
        def get_users(self):
            return self.users.all()

        def get_no_users(self) :
            return self.get_users().count()

        def get_member_groups(self):
            return self.child_groups.all()

        def get_members(self) : 
            members = chain((x for x in self.get_users()), (x for x in self.get_member_groups()))
            return members

        def has_member(self,x) :
            return (x in self.get_members())

        def get_no_members(self) :
            return self.get_no_users() + self.get_member_groups().count()


        def get_permission_agent_name(self) : 
            return self.display_name


        def comment(self, comment, commentor) :
            """ XXX Dummy function. Let's us use permission system to test whether a user has comment 
            permission on a group. What needs to be done, I guess, is to make a comment a dependent type on
            TgGroup and then we'd end up with a create_Comment method on TgGroup which would wrap the call to the 
            comment library."""
            pass

        def is_hub_type(self) :
            return self.group_type == settings.GROUP_HUB_TYPE

        def get_extras(self) :
            # if there are extras for this class, return them
            return self.groupextras
        
        def __str__(self) : 
            return self.display_name        

        child_groups = models.ManyToManyField('self', symmetrical=False, related_name='parent_groups')

        def group_app_label(self):
            from apps.plus_lib.utils import hub_name
            try:
                if self.place.name == settings.VIRTUAL_HUB_NAME:
                    group_label = "group"
                else:
                    group_label = hub_name().lower()
            except Location.DoesNotExist:
                group_label = "group"
            group_app_label = group_label + 's'
            return group_app_label

        @transaction.commit_on_success
        def delete(self) :
 
            sc = self.get_security_context()
            ref = self.get_ref()

            # remove members
            for m in self.get_members() :
                self.remove_member(m)
            
            # remove tags, now moved to GenericReference.delete()

            content_type = ContentType.objects.get_for_model(self)

            # remove statuses
            from apps.microblogging.models import TweetInstance, Tweet, Following

            for ti in TweetInstance.objects.tweets_from(self) :
                ti.delete()
            for ti in TweetInstance.objects.tweets_for(self) :
                ti.delete()

            for t in Tweet.objects.filter(sender_type=content_type, sender_id=self.id) :
                t.delete()
            for f in Following.objects.filter(follower_content_type=content_type,follower_object_id=self.id) :
                f.delete()
            for f in Following.objects.filter(followed_content_type=content_type,followed_object_id=self.id) :
                f.delete() 

            # remove comments
            from threadedcomments.models import ThreadedComment
            for c in ThreadedComment.objects.filter(content_type=content_type, object_id=self.id) :
                c.delete()

            # remove resource (WikiPage)
                
            from apps.plus_wiki.models import WikiPage
            for p in WikiPage.objects.filter(in_agent=ref) :
                p.delete()

            # remove resource (Uploads)
            from apps.plus_resources.models import Resource
            for r in Resource.objects.filter(in_agent=ref) :
                r.delete()


            # permissions
            
            sc.target.clear()

            # a) delete security tags
            for t in sc.get_tags() :
                t.delete()
                # does this delete the relation between other GenRefs and the tag?

            # b) delete this agent as security_context
            sc.delete()

            # remove the genref to this
            ref.delete()

            # remove the group
            super(TgGroup,self).delete()

        def post_save(self) :
            ref = self.get_ref()
            ref.modified = datetime.now()
            ref.display_name = self.get_display_name()
            ref.save()

            
        def save(self):
            super(TgGroup, self).save()
            self.post_save()
   
    
except Exception, e:
    print "##### %s" % e



class User_Group(models.Model):
    class Meta:
        db_table = u'user_group'
    group = models.ForeignKey(TgGroup)
    user = models.ForeignKey(User)
    

# We're going to add the following method to User class (and to group)
def is_member_of(self, group, already_seen=None) :
    if not already_seen:
        already_seen = set([group.id])
    if not group.is_group() : return False
    if group.has_member(self) : return True
    # not a direct member, but perhaps somewhere up the tree of (enclosures / parents)
    for x in self.get_enclosures():
        if x.id not in already_seen:
            already_seen.add(x.id)
        #need to do cycle detection here - since groups can be a member of a any group including a group which is a member of it.
            if x.is_member_of(group, already_seen): 
                return True
    return False
    
# add it to TgGroup too
TgGroup.is_member_of = is_member_of

# to be added to User class
def get_enclosures(self, levels=None) :
    # XXX TO-DO given that this is now different for Users and Groups 
    # no need to have one function assigned to both with a different test
    # just put different versions into respective classes
    """Give us all the things of which this user/group is a member_of
    """
    if levels == None:
        levels = ['member', 'host']

    if isinstance(self, User):
        return self.groups.filter(level__in=levels)
    elif isinstance(self, TgGroup):
        return self.parent_groups.filter(level__in=levels)

TgGroup.get_enclosures = get_enclosures

# set of all enclosures
# to be added to User class


def get_enclosure_set(self) :
    #XXX this needs to stop recursive group membership leading to continual recursion - currently this is implemented in is_member_of
    es = set([self])
    for e in self.get_enclosures() :
        if e != self :
            es = es.union(e.get_enclosure_set())
    return es
    

TgGroup.get_enclosure_set = get_enclosure_set

# to be added to User class
def is_direct_member_of(self, group) :
    return group.has_member(self)

TgGroup.is_direct_member_of = is_direct_member_of

# to be added to User class
def get_permission_agent_name(self) :
    return self.username


from apps.plus_contacts.models import Contact

class MemberInvite(models.Model) :
    invited_content_type = models.ForeignKey(ContentType, related_name='invited_type')
    invited_object_id = models.PositiveIntegerField()
    invited = generic.GenericForeignKey('invited_content_type', 'invited_object_id') # either user or contact

    invited_by = models.ForeignKey(User, related_name='member_is_invited_by')
    group = models.ForeignKey(TgGroup)
    message = models.TextField()
    status = models.IntegerField()

    def make_accept_url(self):
        if self.is_site_invitation():
            url = attach_hmac("/signup/%s/add_member/%s/" % (self.group.id, self.invited.first_name + self.invited.last_name), self.invited_by)
        else:
            url = attach_hmac("/groups/%s/add_member/%s/" % (self.group.id, self.invited.username), self.invited_by)
        return 'http://%s%s' % (settings.DOMAIN_NAME, url)

    def is_site_invitation(self):
        """ Is this an invitation to someone who's not yet a site-member and needs an User / Profile object created"""
        
        if isinstance(self.invited, Contact) and not self.invited.get_user():
            return True
        return False

    def accept_invite(self, sponsor, site_root, **kwargs):
        pass
    
    
def invite_mail(invited, sponsor, invite):
    message = Template(settings.INVITE_EMAIL_TEMPLATE).render(
        Context({'sponsor':sponsor.get_display_name(),
                 'first_name':invited.first_name, 
                 'last_name':invited.last_name}))
    return invited.send_link_email("Invite to join MHPSS", message, sponsor)


def invite_messages(sender, instance, **kwargs):
    from apps.plus_lib.utils import message_user
    if instance is None:
        return
    member_invite = instance
    if member_invite.is_site_invitation():
        invite_mail(member_invite.invited, member_invite.invited_by, member_invite)
    else:
        invite_url = member_invite.make_accept_url()
        if member_invite.message :
            message = """<p>%s</p>""" % member_invite.message
        else :
            message = """
<p>%s is inviting you to join the %s group.</p>
""" % (member_invite.invited_by.get_display_name(), member_invite.group.get_display_name())

            message = message + """
<p><a href="%s">Click here to join %s</a>
""" % (invite_url, member_invite.group.get_display_name())
            
            member_invite.message = message
            member_invite.save()

            from apps.plus_lib.utils import message_user 

            message_user(user, member_invite.invited, 'Invitation to join %s' % member_invite.group.get_display_name(), message, settings.DOMAIN_NAME)
            message_user(user, invited_by, "Invitation sent", """You have invited %s to join %s""" % 
                         (member_invite.invited.get_display_name(), member_invite.group.get_display_name()), settings.DOMAIN_NAME)


if "messages" in settings.INSTALLED_APPS:
    post_save.connect(invite_messages, sender=MemberInvite, dispatch_uid="apps.plus_groups.models")

