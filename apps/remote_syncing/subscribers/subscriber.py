
from bases import WebApp
import simplejson as json


# XXX following shouldn't be hardwired in
url_base = 'http://plusdev.the-hub.net/remote_syncing/' 
                
        
class HubPlusSubscriber(WebApp) :
    
    def __init__(self) :
        pass

    def json_call(url, data) :
        j_data = json.dumps(data) # assume data is dictionary
        
        
    def onUserAdd(self, username, udata):
        url = url_base+'on_create_user'
        

    def onUserMod(self, username, udata):
        url = url_base+'on_user_changed'


    def onGroupAdd(self, group_id, data) :
        url = url_base+'on_create_group'
        
    def onGroupMod(self, group_id, data) :
        url = url_base+'on_group_changed'

    onHubAdd = onGroupAdd
    onHubMod = onGroupMod

    def onJoinGroup(self, username, group_id, data) :
        # doesn't exist yet, 
        url = url_base+'on_join_group'
        
    def onLeaveGroup(self, username, group_id, data) :
        # doesn't exist yet
        url = url_base+'on_leave_group'
