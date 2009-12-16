import ipdb
from apps.plus_tags.models import Tag, tag_add
from apps.plus_lib.utils import bad_name, clean_tag, clean_name
from apps.plus_groups.models import TgGroup
from apps.plus_wiki.models import WikiPage
from apps.plus_resources.models import Resource

print "Bad tags"
for t in Tag.objects.all() :
    if bad_name(t.keyword) :
        print t.keyword.encode('utf-8'),
        new_key = clean_tag(t.keyword)
        if not new_key :
            print "deleting %s" % new_key
            t.delete()
        else :

            ts = Tag.objects.filter(keyword=new_key,tagged_for=t.tagged_for,tag_type=t.tag_type)
            if not ts.count() :
                t.keyword = new_key
                t.save()
            else :
                # use the other tag
                other_tag= ts[0]
                for item in t.items.all() :
                    item.tag = other_tag
                    item.keyword = new_key
                    item.save()
                print 'deleting %s' % t.keyword.encode('utf-8')
                t.delete()
                
 
print "Bad Groups"
for g in TgGroup.objects.all() :
    if bad_name(g.group_name) :
        print g.group_name.encode('utf-8'), clean_name(g.group_name).encode('utf-8'), g.display_name.encode('utf-8')

print "Bad pages"
for p in WikiPage.objects.all() :
    if bad_name(p.name) :
        print p.name.encode('utf-8'), clean_name(p.name).encode('utf-8'), p.title.encode('utf-8')

print "Bad Uploads"
for u in Resource.objects.all() :
    if bad_name(u.name) :
        print u.name.encode('utf-8'), clean_name(u.name).encode('utf-8'), u.title.encode('utf-8')
