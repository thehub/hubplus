from django.contrib.contenttypes.models import ContentType
from django import forms
from django.conf import settings

from models import Service

class LinkForm(forms.Form) :
    text = forms.CharField()
    url = forms.URLField()
    service = forms.ChoiceField(choices=(),required=False)

    def __init__(self, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        self.fields['service'].choices = [(service.id, servive.name) for service in Service.objects.all()]

    def clean_service(self) :
        return None
    
