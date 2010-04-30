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



if __name__ == "__main__":
    patch_db("""ALTER TABLE tg_user ADD "has_avatar" bool; """)

    patch_db("""CREATE TABLE "plus_permissions_genericreference_attachments" (
    "id" serial NOT NULL PRIMARY KEY,
    "from_genericreference_id" integer NOT NULL REFERENCES "plus_permissions_genericreference" ("id") DEFERRABLE INITIALLY DEFERRED,
    "to_genericreference_id" integer NOT NULL REFERENCES "plus_permissions_genericreference" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("from_genericreference_id", "to_genericreference_id")
)
;
 """)

    from django.contrib.auth.models import User
    from apps.avatar.models import Avatar

    for user in User.objects.all() :
        if user.has_avatar : 
            print user, " has avatar"
            continue
        try :
            Avatar.objects.get_for_target(user)
            user.has_avatar = True
            user.save()
            print "updated ", user
        except Avatar.DoesNotExist :
            print "no avatar for ", user
            user.has_avatar=  False
            user.save()
            
