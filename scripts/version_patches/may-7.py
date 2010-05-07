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
    patch_db("""ALTER TABLE tg_user ADD "post_or_zip" varchar(30); """)
