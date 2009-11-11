from psn_import.utils import stop_words, substitutes, strip_out

from apps.plus_tags.models import Tag
import ipdb
import re

reg = re.compile('\W')

for t in Tag.objects.all() :
    
    if substitutes.has_key(t.keyword) :
        print "substituting %s for %s" % (t.keyword,substitutes[t.keyword])
        t.keyword  = substitutes[t.keyword]
        t.save()
    elif t.keyword in stop_words :
        print "deleting %s"%t.keyword, 
        t.delete()
    elif not t.keyword :
        print 'deleting empty tag %s , %s' % (t.id, t.keyword)


    if t.tag_type == 'folder' :
        t.tag_type = ''
        t.save()

    if reg.search(t.keyword) :
        print "found non alpha %s" % t.keyword.encode('utf-8')
        t.keyword = strip_out(t.keyword)
        t.save()
        #ipdb.set_trace()


