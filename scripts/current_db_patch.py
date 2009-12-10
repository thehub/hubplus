
from scripts.db_patch_lib import patch_hubspace

patch = """

alter table plus_wiki_wikipage add column copyright_holder varchar(100);

"""

patch_hubspace(patch)
