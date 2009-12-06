from django import forms
from microblogging.models import Tweet, tweet, send_tweet
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

try:
    from notification import models as notification
except ImportError:
    notification = None

class TweetForm(forms.ModelForm):
    
    text = forms.CharField(label='',
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols':'30',
            'id':'new_tweet'
        }))

    sender_class = forms.CharField()
    sender_id = forms.CharField()
    
    class Meta:
        model = Tweet
        exclude = ('sender_type', 'sender_id', 'sent')
        
    def __init__(self, user=None, *args, **kwargs):
        super(TweetForm, self).__init__(*args, **kwargs)
        
    def clean_text(self):
        return self.cleaned_data['text'].strip()

    def clean(self) :
        cls = self.cleaned_data['sender_class']
        id = self.cleaned_data['sender_id']
        cts = ContentType.objects.filter(name=cls) 
        if not cts :
            raise forms.ValidationError(_('No class called %(class_name)s') % {'class_name' : cls})
        self.sender = cts[0].get_object_for_this_type(id=id)
        return self.cleaned_data
        
    def save(self):
        send_tweet(self.sender,self.cleaned_data["text"])


        
