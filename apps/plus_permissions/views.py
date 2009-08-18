from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.db import transaction
from django.utils import simplejson

    def json_slider_group(self, title, intro, resource, interfaces, mins, constraints) :
        owner = self.get_owner(resource)
        creator = self.get_creator(resource)
        ps = self.get_permission_system()

        group_type = ContentType.objects.get_for_model(ps.get_anon_group())

        options = self.make_slider_options(resource,owner,creator)

        option_labels = [o.name for o in options]
        option_types = [ContentType.objects.get_for_model(o.agent) for o in options]
        option_ids = [o.agent.id for o in options]

        resource_type = ContentType.objects.get_for_model(resource)
        json = {
          'title':title,
          'intro':intro,
          'resource_id':resource.id,
          'resource_type':resource_type.id,
          'option_labels':option_labels,
          'option_types':[type.id for type in option_types],
          'option_ids':option_ids,
          'sliders':interfaces,
          'interface_ids':[ps.get_interface_id(resource.__class__,i) for i in interfaces],
          'mins':mins,
          'constraints':constraints,
          'extras': {} # use for non-slider permissions
          }


        current=[]
        for i in json['interface_ids'] :
            for s in SecurityTag.objects.filter(interface=i,resource_content_type=resource_type,resource_object_id=resource.id) :
                if s.agent in [o.agent for o in options] :
                    # we've found a SecurityTag which maps one of the agents on the slider, therefore 
                    # it's THIS agent which is the official slider setting
                    # map from this agent to position on the slider
                    j=0
                    agent_type = ContentType.objects.get_for_model(s.agent)
                    for (typ,ids) in zip(option_types,option_ids) :
                        if (typ==agent_type and ids==s.agent.id) :
                            current.append(j)
                            break
                        j=j+1            

        json['current'] = current
        return simplejson.dumps({'sliders':json})




@login_required
def update_main_permission_sliders(request,username) :
    ps = get_permission_system()
    pm = ps.get_permission_manager(Profile)
    p = request.user.get_profile()

    form = request.form()
    json = pm.main_json_slider_group(p)
    print json
    return HttpResponse(json, mimetype='text/plain')


class NoSliderException(Exception) :
    def __init__(self,cls,name) :
        self.cls = cls
        self.name = name


