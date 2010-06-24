import psycopg2
import local_settings as db_config

def patch_db(patch):
    con = getPostgreSQLConnection()
    cur = con.cursor()
    try:
        cur.execute(patch)
        con.commit()
    except Exception, e:
        print `e`


def getPostgreSQLConnection():

    user = db_config.DATABASE_USER
    password = db_config.DATABASE_PASSWORD
    host = db_config.DATABASE_HOST and db_config.DATABASE_HOST or 'localhost'
    dbname = db_config.DATABASE_NAME
    con = psycopg2.connect("host=%(host)s user=%(user)s password=%(password)s dbname=%(dbname)s" %{'host':host,
                                                                                                   'user':user,
                                                                                                   'password':password,
                                                                                                   'dbname':dbname})
    return con

# some cleaning up

from django.contrib.auth.models import User
from apps.plus_permissions.default_agents import get_all_members_group




def various_db() :
    patch_db('alter table location add hidden boolean default false;')
    patch_db('alter table microblogging_following add event_type integer;')
    patch_db('alter table microblogging_following add cc_to_email boolean default false;')
    patch_db('alter table microblogging_following add opt_out boolean default false;')



def unhost(username) :
    if User.objects.filter(username=username) :
        u = User.objects.get(username=username)
        for group in u.get_enclosures() :
            if group.id != get_all_members_group().id :
                group.remove_member(u)



various_db()

##unhost('manfred.meyer')
#unhost('synnove.fredericks')


