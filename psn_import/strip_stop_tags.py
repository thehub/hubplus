from psn_import.utils import stop_words, substitutes 

from apps.plus_tags.models import Tag

for t in Tag.objects.all() :
    
    if substitutes.has_key(t.keyword) :
        print "substituting %s for %s" % (t.keyword,substitutes[t.keyword])
        t.keyword  = substitutes[t.keyword]
        t.save()
    elif t.keyword in stop_words :
        print "deleting %s"%t.keyword, 
        t.delete()
        

