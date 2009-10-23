from psn_import.utils import strip_out, stop_words
from apps.plus_tags.models import Tag


for t in Tag.objects.all() :
    t.keyword = strip_out(t.keyword)
    print t.keyword.encode('utf-8')
    #t.save()
    if t.keyword in stop_words :
        import ipdb
        ipdb.set_trace()
        t.delete()
