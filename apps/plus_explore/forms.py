from django import forms
from django.utils.translation import ugettext_lazy as _


ORDERS = (
    ('name', _('A-Z')),
    ('relevance', _('Relevance')),
    ('date', _('Recently Created')),
    ('modified', _('Recently Modified'))
)

AREAS = (
    ('regions:groups', _('Regions')),
    ('hubs:groups', _('Hubs')),
    ('groups:groups', _('Groups')),
    ('profile_list', _('Members'))
)

class SearchForm(forms.Form):
    search = forms.CharField(required=False)
    order = forms.ChoiceField(required=False, choices=ORDERS)
    current_area = forms.ChoiceField(required=False, choices=AREAS)
