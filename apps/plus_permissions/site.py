from django.db import models


class Site(models.Model) :
    """ An object that represents the whole site. 
    Creation of entities which don't, themselves, belong to another agent will now be done by this object"""
    pass
