from psn_import.utils import stop_words, substitutes 

from apps.plus_tags.models import Tag
import ipdb

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
    

