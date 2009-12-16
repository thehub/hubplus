from django import forms
from django.utils.translation import ugettext_lazy as _
from apps.plus_lib.utils import tag_validation_regex_str
from apps.plus_tags.models import tag_stop_words
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
    tag_value = forms.RegexField(min_length=2, max_length=20, regex=tag_validation_regex_str(), error_messages={'invalid':_("Invalid tag name. Tags can contain alphanumeric values and . _ and have a maximum length of 20 characters")})


    def clean_tag_value(self) :
        # assiming that the RegEx field already filtered according to our criteria, just want to remove the stop-words
        if self.data['tag_value'] in tag_stop_words :
            raise forms.ValidationError(_("Your tag was not considered sufficiently distinct or meaningful."))
        return self.data['tag_value']
