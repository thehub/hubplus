from django.db import models

# Create your models here.

class VirtualField(object) :
    def __get__(self,obj,type=None) : return "%s %s"% (obj.x,obj.y)
    def __set__(self,obj,val) :
        xs = val.split(' ')
        obj.x = xs[0]
        obj.y = xs[1]
    def __delete__(self,obj) : pass


class MyTestClass(models.Model) :
    x = models.CharField(max_length=20)
    y = models.CharField(max_length=20)
    both = VirtualField()

