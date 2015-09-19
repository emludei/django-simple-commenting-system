from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from comments.models import Comment


COMMENTS_MAX_LENGTH = getattr(settings, 'COMMENTS_MAX_LENGTH', 6000)


class CommentForm(forms.ModelForm):
    comment = forms.CharField(label=_('Comment'), max_length=COMMENTS_MAX_LENGTH, widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = '__all__'
