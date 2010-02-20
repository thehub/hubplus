from django.db import models
import pickle

class SyncerSession(models.Model) :
    key = models.CharField(max_length=256)
    data = models.TextField()

    def set_data(self,val) :
        self.data = val # = pickle.dumps(val)

    def get_data(self):
        return self.data # pickle.loads(self.data)

class DbSessions(object) :
    def has_key(self,key) :
        return SyncerSession.objects.filter(key=key).count() > 0

    def __getitem__(self,key) :
        ss = SyncerSession.objects.get(key=key)
        return ss.get_data()
    
    def get(self,key,default) :
        if self.has_key(key) : 
            return self[key]
        return default

    def __setitem__(self,key,val):
        ss,created = SyncerSession.objects.get_or_create(key=key)
        ss.set_data(val)
        ss.save()


    def __repr__(self) :
        return ', '.join(['(%s : %s)' % (x.key,x.data) for x in SyncerSession.objects.all()])

def get_sessions() :
    return DbSessions()
