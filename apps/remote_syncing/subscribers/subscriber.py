
from bases import WebApp
import simplejson as json


# XXX following shouldn't be hardwired in
url_base = 'http://plusdev.the-hub.net/remote_syncing/' 
                
# presumably WebApps can handle the signing-in / cookie session for us??

class HubPlusSubscriber(WebApp) :

    def post(self, event, **kwargs) :
        # this is a placeholder
        # to-do
        # 1) make sure this is a real POST ... not sure if makeHttpReq is
        # 2) handle if error comes back ({'OK':False,'msg':'error message'})
        return self.makeHttpReq(url_base+event, {'json':json.dumps(kwargs)})

    def onUserAdd(self, username, udata):
        cj,result = self.post('on_create_user', username=username)


    def onUserMod(self, username, udata):
        cj,result = self.post('on_user_changed', username=username)


    def onGroupAdd(self, group_id, data) :
        cj,result = self.post('on_create_group', group_id=group_id)
        
    def onGroupMod(self, group_id, data) :
        cj,result = self.post('on_group_changed', group_id=group_id)

    onHubAdd = onGroupAdd
    onHubMod = onGroupMod

    def onJoinGroup(self, username, group_id, data) :
        # need to create this event
        cj,result = self.post('on_join_group',username=username,group_id=group_id)
        
    def onLeaveGroup(self, username, group_id, data) :
        # need to create this event
        cj,result = self.post('on_leave_group',username=username,group_id=group_id)
