from psn_import.utils import load_all, reverse, maps, get_group_for, get_top_container, title as e_title
from psn_import.utils import get_matching_id

from apps.plus_resources.models import Resource


for res in Resource.objects.filter(stub=False) :
    print res.title.encode('utf-8'), res.created_by
    if not res.created_by :
        import ipdb
        ipdb.set_trace()
