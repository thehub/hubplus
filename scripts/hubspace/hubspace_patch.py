#!/usr/bin/python

import psycopg2
import local_settings as db_config

def patch_hubspace(patch):
    con = getPostgreSQLConnection()
    cur = con.cursor()
    try:
        cur.execute(patch)
        con.commit()
    except Exception, e:
        print `e`


def getPostgreSQLConnection():
    """ Create a connection to the PostgreSQL database 
    """
    user = db_config.DATABASE_USER
    password = db_config.DATABASE_PASSWORD
    host = db_config.DATABASE_HOST and db_config.DATABASE_HOST or 'localhost'  #+ ':' + db_config.DATABASE_PORT
    dbname = db_config.DATABASE_NAME
    con = psycopg2.connect("host=%(host)s user=%(user)s password=%(password)s dbname=%(dbname)s" %{'host':host, 'user':user, 'password':password, 'dbname':dbname})
    return con


sql_patch = """
ALTER TABLE tg_user ADD "username" varchar(30) ; -- NOT NULL UNIQUE;
ALTER TABLE tg_user ADD "email" varchar(75) ; -- NOT NULL,
ALTER TABLE tg_user ADD "is_staff" bool ; -- NOT NULL, 
ALTER TABLE tg_user ADD "is_active" bool ; -- NOT NULL, 
ALTER TABLE tg_user ADD "is_superuser" bool  ; -- NOT NULL, 
ALTER TABLE tg_user ADD "last_login" date  ; -- NOT NULL, 
ALTER TABLE tg_user ADD "date_joined" date  ; -- NOT NULL, 
ALTER TABLE tg_user ADD "place" character varying(150);
ALTER TABLE tg_user ADD "homehub_id" integer;
CREATE INDEX "tg_user_homehub_id" on tg_user (homehub_id);
CREATE INDEX "tg_user_homeplace_id" on tg_user (homeplace_id);
ALTER TABLE "tg_user" ADD FOREIGN KEY (homehub_id) REFERENCES tg_group(id) DEFERRABLE INITIALLY DEFERRED;
Alter Table tg_user ADD "psn_id" varchar(100);
Alter Table tg_user ADD "psn_password_hmac_key" varchar(100);
Alter Table tg_user ADD "cc_messages_to_email" boolean; -- NOT NULL;

update tg_user set username = user_name;
update tg_user set email = email_address;
update tg_user set is_staff = false, is_active = true, is_superuser = false;

CREATE TABLE "tg_user_user_permissions" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "tg_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "permission_id")
)
;
"""



patch2 = """
Alter Table tg_group ADD "psn_id" varchar(100);
Alter Table tg_group ADD "path" varchar(120);
Alter Table tg_group ADD "about" text;
Alter Table tg_group ADD "group_type" varchar(30);
Alter Table tg_group ADD "title" varchar(60);
Alter Table tg_group ADD "description" text;
Alter Table tg_group ADD "body" text;
Alter Table tg_group ADD "rights" text;
Alter Table tg_group DROP CONSTRAINT "tg_group_level_check";
Alter Table tg_group ADD CONSTRAINT "tg_group_level_check" CHECK (level::text = ANY (ARRAY['superuser'::character varying, 'director'::character varying, 'member'::character varying, 'host'::character varying, 'public'::character varying]::text[]));
ALTER TABLE "tg_group" ADD COLUMN "active" boolean default True NOT NULL;
"""

patch3 = """
CREATE TABLE "tg_group_child_groups" (
    "id" serial NOT NULL PRIMARY KEY,
    "from_tggroup_id" integer NOT NULL REFERENCES "tg_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    "to_tggroup_id" integer NOT NULL REFERENCES "tg_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("from_tggroup_id", "to_tggroup_id")
);
"""


patch4 = """
Alter table tg_group add column address character varying(255);
"""

patch5 = """
Alter Table tg_user ADD "country" varchar(2);
"""

patch6 = """
ALTER TABLE plus_permissions_genericreference ALTER COLUMN "permission_prototype" TYPE varchar(20);
"""


def main():
    patch_hubspace(sql_patch)
    patch_hubspace(patch2)
    patch_hubspace(patch3)
    patch_hubspace(patch4)
    patch_hubspace(patch5)
    patch_hubspace(patch6)

if __name__ == "__main__":
    main()
