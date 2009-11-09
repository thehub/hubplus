from psn_import.utils import load_all, reverse, maps, get_group_for

load_all()

def check_group(lst) :
    for group in lst :
        obj_group = get_group_for(group['uid'])
        print group['groupname'], obj_group.get_display_name()

    
if __name__ == '__main__' :
    check_group(maps['Group'])
    check_group(maps['Hub'])
