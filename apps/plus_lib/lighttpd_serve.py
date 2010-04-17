from django.conf import settings
import os, mimetypes
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.utils.http import http_date
import stat

# new lightty serving

PINAX_MEDIA_ROOT = os.path.join(settings.PINAX_ROOT, 'media', settings.PINAX_THEME)
WEBSERVER_MEDIA_ROOT = getattr(settings, 'WEBSERVER_MEDIA_ROOT',PINAX_MEDIA_ROOT)


def get_path_from_webserver(file_path) :
    # XXXX this is a horrible hack ... please find a better way of doing this
    pieces = file_path.split('site_media/')
    new_path = WEBSERVER_MEDIA_ROOT + pieces[1]
    return new_path


def file_exists(fullpath) :
    if fullpath is None:
        raise Http404, '"%s" does not exist' % path
    if not os.path.exists(fullpath):
        raise Http404, '"%s" does not exist' % path
    if os.path.isdir(fullpath):
        raise Http404, "Directory indexes are not allowed here."
    return True

def get_mimetype(path) :
    return mimetypes.guess_type(path)[0] or 'application/octet-stream'

def get_last_modified(path) :
   statobj = os.stat(path)
   return http_date(statobj[stat.ST_MTIME])


def send_file(path, file_size, mimetype, last_modified) :
    response = HttpResponse(mimetype=mimetype)
    response["Last-Modified"] = last_modified
    response["Content-Length"] = file_size
    response['X-Sendfile'] = path

    new_filename=path.split('/')[-1]
    response['Content-Disposition'] = 'attachment;filename=%s'%new_filename

    return response

