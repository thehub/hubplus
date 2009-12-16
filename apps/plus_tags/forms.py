from django import forms
from django.utils.translation import ugettext_lazy as _

choices = (
    ('tag','tag'),
    ('interests','interests'),
    ('skills','skills'),
    ('needs','needs'),
    ('',''),
)

class AddTagForm(forms.Form):
    tagged_class = forms.CharField(max_length=100)
    tagged_id = forms.IntegerField()
    tag_type = forms.ChoiceField(choices=choices)
    #should match the regex in plus_explore.urls.explore_filtered apart from the '+' sign being excluded
    tag_value = forms.RegexField(min_length=2, max_length=20, regex="^[ \w\._-]*$", error_messages={'invalid':_("Invalid tag name. Tags can contain alphanumeric values and . _ - and have a maximum length of 20 characters")})

    
