# vim:ts=2:sw=2:et
#
# Django Default 403.html handler
# http://wtanaka.com/django/django403
#
# Copyright (C) 2009 Wesley Tanaka <http://wtanaka.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import django.http
import django.template

class Django403Middleware(object):
  """Replaces vanilla django.http.HttpResponseForbidden() responses
  with a rendering of 403.html
  """
  def process_response(self, request, response):
    # If the response object is a vanilla 403 constructed with
    # django.http.HttpResponseForbidden() then call our custom 403 view
    # function
    if isinstance(response, django.http.HttpResponseForbidden) and \
        set(dir(response)) == set(dir(django.http.HttpResponseForbidden())):
      import views
      try:
        return views.access_denied(request)
      except django.template.TemplateDoesNotExist, e:
        return views.fallback_403(request)

    return response
