from django import forms
from django.utils.translation import ugettext_lazy as _


ORDERS = (
    ('display_name', _('A-Z')),
    ('relevance', _('Relevance')),
    ('modified', _('Most recent')),
)

AREAS = (
    ('regions:groups', _('Regions')),
    ('hubs:groups', _('Hubs')),
    ('groups:groups', _('Groups')),
    ('profile_list', _('Members')),
    ('resources', _('Resources'))
)

class SearchForm(forms.Form):
    search = forms.CharField(required=False)
    order = forms.ChoiceField(required=False, choices=ORDERS)
    current_area = forms.ChoiceField(required=False, choices=AREAS)
