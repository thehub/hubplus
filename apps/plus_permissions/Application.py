
from models import Interface, InterfaceReadProperty, InterfaceCallProperty, get_permission_system

from apps.plus_contacts.models import Application

# === permission interfaces

class ApplicationViewer(Interface) : 
    pk = InterfaceReadProperty('pk')

    applicant_content_type = InterfaceReadProperty('applicant_content_type')
    applicant_object_id = InterfaceReadProperty('applicant_object_id')
    applicant = InterfaceReadProperty('applicant')
    
    group = InterfaceReadProperty('group')
    request = InterfaceReadProperty('request')
    status = InterfaceReadProperty('status')

    admin_comment = InterfaceReadProperty('admin_comment')
    date = InterfaceReadProperty('date')

    @classmethod
    def get_id(self) : 
        return 'Application.Viewer'



get_permission_system().add_interface('Application','Viewer',ApplicationViewer)


