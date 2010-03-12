#!/usr/bin/python

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
    """ Create a connection to the PostgreSQL database    """
    user = db_config.DATABASE_USER
    password = db_config.DATABASE_PASSWORD
    host = db_config.DATABASE_HOST and db_config.DATABASE_HOST or 'localhost'  #+ ':' + db_config.DATABASE_PORT 
    dbname = db_config.DATABASE_NAME
    con = psycopg2.connect("host=%(host)s user=%(user)s password=%(password)s dbname=%(dbname)s" %
                           {'host':host, 
                            'user':user, 
                            'password':password, 
                            'dbname':dbname})
    return con


if __name__ == '__main__' :
    patch_db("""ALTER TABLE tg_user ADD "active" integer DEFAULT 1;""")
    patch_db("""ALTER TABLE plus_groups_memberinvite DROP COLUMN "invited_content_type";""")
    patch_db("""ALTER TABLE plus_groups_memberinvite ADD "invited_content_type_id" integer;""")

    patch_db("""ALTER TABLE plus_groups_memberinvite ADD "invited_object_id" integer;""")
    patch_db("""ALTER TABLE plus_groups_memberinvite DROP COLUMN "invited_id";""")
    patch_db("""ALTER TABLE plus_group DROP COLUMN "users";""")
    
    patch_db("""ALTER TABLE plus_contacts_contact ADD "user_id" integer;""")
    patch_db("""ALTER TABLE plus_contacts_contact DROP COLUMN "invited_by";""")





