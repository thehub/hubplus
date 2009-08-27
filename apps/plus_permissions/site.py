from django.db import models


class Site(models.Model) :
    """ An object that represents the whole site. 
    Creation of entities which don't, themselves, belong to another agent will now be done by this object"""
    
    def create_group(self, group_name, display_name, place=None, level=None, user=None) :
        return get_or_create(group_name=None, display_name=None, place=None, level=None, user=None)


        
