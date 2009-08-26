from datetime import datetime, timedelta

from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _, ugettext

from django.contrib.sites.models import Site


class TgGroupForm(forms.Form):
    
    def clean_XXX(self):
        if (OK) :
            return (XXX)
        else:
            raise forms.ValidationError("XXX invalid message")



