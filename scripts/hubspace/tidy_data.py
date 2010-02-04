from apps.plus_groups.models import TgGroup
from apps.plus_permissions.default_agents import get_or_create_root_location

def tidy_groups():
    hub_members_groups = TgGroup.objects.filter(level='member').exclude(place=get_or_create_root_location())
    for hub in hub_members_groups:
        hub.group_name = hub.group_name.replace('_', ' ')
        hub.group_type = 'hub'
        hub.save()

def main():
    tidy_groups()

if __name__ == '__main__':
    main()
