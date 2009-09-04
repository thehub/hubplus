import simplejson as json

from django.http import HttpResponse


def json_view(func):
    def wrap(req, *args, **kwargs):
        try:
            #j = json.loads(req.raw_post_data)
            j = json.loads(req.POST['json'])
        except ValueError:
            j = None

        resp = func(req, j, *args, **kwargs)

        if isinstance(resp, HttpResponse):
            return resp

        return HttpResponse(json.dumps(resp), mimetype="application/json")

    return wrap
