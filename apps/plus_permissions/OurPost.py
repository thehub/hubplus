from django.db import models

class OurPost(models.Model):
    title = models.CharField(max_length='20')
    body = models.CharField(max_length='20')

    def __str__(self):
        return "OurPost %s,%s" % (self.title,self.body)

    def foo(self):
        pass
