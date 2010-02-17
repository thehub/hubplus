from django.db import models


class Site(models.Model) :
    """ An object that represents the whole site. 
    Creation of entities which don't, themselves, belong to another agent will now be done by this object"""

    def create_hub(self, *args, **kwargs) :
        from apps.plus_groups.models import Location
        from django.conf import settings

        place,created = Location.objects.get_or_create(name=kwargs['location_name'])

        group = self.create_TgGroup(
            group_name=kwargs['group_name'],
            display_name=kwargs['display_name'],
            group_type = settings.GROUP_HUB_TYPE,
            level = 'member',
            user = kwargs['user'],
            description = kwargs['description'],
            permission_prototype = kwargs['permission_prototype'],
            place = place,
            )
        group.save()
        directors = self.create_TgGroup(
            group_name=group.group_name + '_directors',
            display_name=group.display_name+' Directors',
            group_type='administrative',
            level='director',
            place=place,
            user=kwargs['user'],
            description = 'Directors of %s' % group.display_name,
            permission_prototype='private',
            )
        directors.save()

        from apps.synced import post_location_add
        post_location_add.send(sender=place, location = place)
                
        return group


    def create_virtual(self, *args, **kwargs) :
        del kwargs['place']
        
        return self.create_TgGroup(*args, **kwargs)
