
class Counter(dict) :
    def __call__(self,key):
        if not self.has_key(key) :
            self[key]=0
        self[key]=self[key]+1
